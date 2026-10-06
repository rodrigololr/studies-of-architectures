"""
use_cases/interactors.py - Camada 2: Interactor de Enriquecimento e Qualificação de Leads.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from entities.models import Lead, LeadQualification, RepTier
from use_cases.dto import IngestLeadRequestModel, IngestLeadResponseModel
from use_cases.boundaries import (
    IngestLeadInputBoundary,
    IngestLeadOutputBoundary,
    LeadRepositoryGateway,
    FirmographicEnrichmentGateway,
    SalesRepRepositoryGateway,
)


class IngestLeadInteractor(IngestLeadInputBoundary):
    def __init__(
        self,
        lead_repo: LeadRepositoryGateway,
        firmographic_gateway: FirmographicEnrichmentGateway,
        rep_repo: SalesRepRepositoryGateway,
        presenter: IngestLeadOutputBoundary,
    ) -> None:
        self.lead_repo = lead_repo
        self.firmographic_gateway = firmographic_gateway
        self.rep_repo = rep_repo
        self.presenter = presenter

    def execute(self, request: IngestLeadRequestModel) -> None:
        lead_id = f"lead_{uuid.uuid4().hex[:8]}"
        lead = Lead(
            lead_id=lead_id,
            contact_name=request.name,
            corporate_email=request.corporate_email,
            company_name=request.company_name,
            job_title=request.job_title,
            created_at=datetime.now(timezone.utc),
        )

        # 1. Regra de Domínio: E-mail Corporativo Obrigatório
        if not lead.validate_corporate_domain():
            self.presenter.present(IngestLeadResponseModel(
                success=False,
                lead_id=None,
                company_name=request.company_name,
                score=0,
                qualification=LeadQualification.COLD.value,
                assigned_sales_rep=None,
                employee_count=0,
                annual_revenue=0.0,
                message=f"E-mail '{request.corporate_email}' não corporativo (domínios públicos não são aceitos).",
            ))
            return

        # 2. Enriquecimento Firmográfico Externo (Gateway)
        employees, revenue = self.firmographic_gateway.lookup_company(request.company_name)
        lead.employee_count = employees
        lead.annual_revenue_usd = revenue

        # 3. Cálculo de Score e Qualificação na Entidade
        score, qualification = lead.calculate_qualification_score()

        # 4. Atribuição de Vendedor por Tier de Qualificação
        if qualification == LeadQualification.HOT:
            target_tier = RepTier.ENTERPRISE
        elif qualification == LeadQualification.WARM:
            target_tier = RepTier.MID_MARKET
        else:
            target_tier = RepTier.SMB

        rep = self.rep_repo.find_available_by_tier(target_tier)
        rep_name = "Automação / Fila Geral"
        if rep:
            lead.assigned_rep_id = rep.rep_id
            rep_name = f"{rep.name} ({rep.tier.value})"

        # 5. Persistência
        self.lead_repo.save(lead)

        # 6. Apresentação (Output Boundary)
        self.presenter.present(IngestLeadResponseModel(
            success=True,
            lead_id=lead.lead_id,
            company_name=lead.company_name,
            score=score,
            qualification=qualification.value,
            assigned_sales_rep=rep_name,
            employee_count=employees,
            annual_revenue=revenue,
            message=f"Lead {lead.contact_name} enriquecido com sucesso! Score: {score} pts ({qualification.value}).",
        ))
