"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Tuple


class LeadQualification(str, Enum):
    HOT = "HOT"      # Pronto para fechamento imediato
    WARM = "WARM"    # Em maturação / Oportunidade ativa
    COLD = "COLD"    # Baixo fit / Nutrição automatizada


class RepTier(str, Enum):
    ENTERPRISE = "ENTERPRISE"
    MID_MARKET = "MID_MARKET"
    SMB = "SMB"


@dataclass(frozen=True)
class SalesRep:
    rep_id: str
    name: str
    tier: RepTier
    is_active: bool = True


@dataclass
class Lead:
    lead_id: str
    contact_name: str
    corporate_email: str
    company_name: str
    job_title: str
    employee_count: int = 0
    annual_revenue_usd: float = 0.0
    score: int = 0
    qualification: LeadQualification = LeadQualification.COLD
    assigned_rep_id: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)

    def validate_corporate_domain(self) -> bool:
        """Regra Corporativa: Rejeita e-mails genéricos gratuitos."""
        free_domains = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com"}
        domain = self.corporate_email.split("@")[-1].lower() if "@" in self.corporate_email else ""
        return domain not in free_domains and "." in domain

    def calculate_qualification_score(self) -> Tuple[int, LeadQualification]:
        """
        Regra Corporativa de Negócio:
        Calcula pontuação do Lead baseada em porte da empresa, faturamento e senioridade do contato.
        """
        points = 0

        # 1. Porte de Funcionários
        if self.employee_count >= 500:
            points += 40
        elif self.employee_count >= 100:
            points += 25
        elif self.employee_count >= 20:
            points += 15
        else:
            points += 5

        # 2. Faturamento Anual Estimado
        if self.annual_revenue_usd >= 10_000_000.0:
            points += 30
        elif self.annual_revenue_usd >= 1_000_000.0:
            points += 20
        else:
            points += 5

        # 3. Nível Hierárquico do Contato
        title_lower = self.job_title.lower()
        if any(keyword in title_lower for keyword in ["cto", "ceo", "cfo", "vp", "vice president", "diretor"]):
            points += 30
        elif any(keyword in title_lower for keyword in ["gerente", "manager", "head", "lead"]):
            points += 20
        elif any(keyword in title_lower for keyword in ["coordenador", "supervisor"]):
            points += 10
        else:
            points += 5

        self.score = points
        if points >= 80:
            self.qualification = LeadQualification.HOT
        elif points >= 50:
            self.qualification = LeadQualification.WARM
        else:
            self.qualification = LeadQualification.COLD

        return points, self.qualification
