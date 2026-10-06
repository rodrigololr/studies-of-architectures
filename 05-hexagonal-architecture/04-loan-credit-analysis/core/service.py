"""
service.py - Núcleo da Aplicação (Core / Hexágono) para Análise de Risco de Crédito.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from domain.models import (
    LoanProposal,
    CreditAnalysisResult,
    CreditDecision,
    RiskRating,
)
from domain.exceptions import (
    InvalidProposalException,
    BureauUnavailableException,
)
from ports.driver import (
    UnderwriteCreditProposalUseCasePort,
    GetCreditDossierUseCasePort,
)
from ports.driven import (
    CreditBureauPort,
    CentralBankScrPort,
    InterestRatePolicyPort,
    CreditDossierRepositoryPort,
)


class CreditUnderwritingService(UnderwriteCreditProposalUseCasePort, GetCreditDossierUseCasePort):
    def __init__(
        self,
        bureaus: List[CreditBureauPort],
        bacen_scr: CentralBankScrPort,
        rate_policy: InterestRatePolicyPort,
        dossier_repo: CreditDossierRepositoryPort,
    ) -> None:
        self.bureaus = bureaus
        self.bacen_scr = bacen_scr
        self.rate_policy = rate_policy
        self.dossier_repo = dossier_repo

    def evaluate(self, proposal: LoanProposal) -> CreditAnalysisResult:
        # 1. Validações preliminares de negócio
        if proposal.requested_amount <= 0:
            raise InvalidProposalException("Valor solicitado deve ser superior a zero.")

        if not (6 <= proposal.installments_count <= 360):
            raise InvalidProposalException("Prazo de parcelamento deve estar entre 6 e 360 meses.")

        if proposal.applicant.monthly_income <= 0:
            raise InvalidProposalException("Renda mensal comprovada deve ser positiva.")

        # 2. Consulta de Birôs de Crédito (Driven Ports)
        bureau_scores: List[int] = []
        has_negative_records = False

        for bureau in self.bureaus:
            score_data = bureau.query_score(proposal.applicant.cpf)
            if score_data:
                bureau_scores.append(score_data.score)
                if score_data.has_active_defaults:
                    has_negative_records = True

        if not bureau_scores:
            raise BureauUnavailableException("Nenhum birô de crédito respondeu à verificação de score.")

        avg_score = sum(bureau_scores) // len(bureau_scores)

        # 3. Consulta de Endividamento no Banco Central SCR (Driven Port)
        existing_commitments = self.bacen_scr.get_total_financial_commitments(proposal.applicant.cpf)

        reasons: List[str] = []

        # 4. Avaliação de Restrições Críticas
        if has_negative_records:
            reasons.append("Restrição cadastral: Inadimplência ativa apontada em birôs de crédito.")
            return self._record_and_return_rejection(proposal, reasons, RiskRating.B)

        if avg_score < 400:
            reasons.append(f"Score de crédito muito baixo ({avg_score} pts). Mínimo exigido: 400 pts.")
            return self._record_and_return_rejection(proposal, reasons, RiskRating.B)

        # 5. Classificação do Rating de Risco
        if avg_score >= 850:
            risk = RiskRating.AAA
        elif avg_score >= 700:
            risk = RiskRating.AA
        elif avg_score >= 550:
            risk = RiskRating.A
        else:
            risk = RiskRating.B

        # 6. Determinação de Taxa e Cálculo da Parcela (Tabela Price)
        annual_rate = self.rate_policy.get_annual_rate(risk)
        monthly_rate = (annual_rate / 100.0) / 12.0

        n = proposal.installments_count
        pv = proposal.requested_amount
        if monthly_rate > 0:
            monthly_pmt = pv * (monthly_rate / (1.0 - (1.0 + monthly_rate) ** (-n)))
        else:
            monthly_pmt = pv / n

        monthly_pmt = round(monthly_pmt, 2)

        # 7. Regra Bacen: Comprometimento de Renda Máximo de 30%
        income_limit = round(proposal.applicant.monthly_income * 0.30, 2)
        if monthly_pmt > income_limit:
            reasons.append(
                f"Capacidade de pagamento insuficiente: Parcela calculada (R$ {monthly_pmt:.2f}) "
                f"excede 30% da renda líquida comprovada (Teto: R$ {income_limit:.2f})."
            )
            return self._record_and_return_rejection(proposal, reasons, risk)

        # 8. Aprovação Concedida
        reasons.append(f"Score satisfatório ({avg_score} pts). Renda e capacidade financeira aderentes.")
        result = CreditAnalysisResult(
            proposal_id=proposal.proposal_id,
            decision=CreditDecision.APPROVED,
            risk_rating=risk,
            approved_amount=proposal.requested_amount,
            monthly_installment=monthly_pmt,
            annual_interest_rate=annual_rate,
            reasons=reasons,
            analyzed_at=datetime.now(timezone.utc),
        )

        self.dossier_repo.save(result)
        return result

    def _record_and_return_rejection(
        self,
        proposal: LoanProposal,
        reasons: List[str],
        risk: RiskRating,
    ) -> CreditAnalysisResult:
        result = CreditAnalysisResult(
            proposal_id=proposal.proposal_id,
            decision=CreditDecision.REJECTED,
            risk_rating=risk,
            approved_amount=0.0,
            monthly_installment=0.0,
            annual_interest_rate=0.0,
            reasons=reasons,
            analyzed_at=datetime.now(timezone.utc),
        )
        self.dossier_repo.save(result)
        return result

    def get_dossier(self, proposal_id: str) -> Optional[CreditAnalysisResult]:
        return self.dossier_repo.find_by_proposal_id(proposal_id)
