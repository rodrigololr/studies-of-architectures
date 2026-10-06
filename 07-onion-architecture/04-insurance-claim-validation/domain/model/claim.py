"""Entidade de Sinistro (Claim) e Decisão de Regulação."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from .damage_assessment import DamageAssessment
from .exceptions import InvalidClaimStateException


class ClaimStatus(Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FRAUD_SUSPECTED = "FRAUD_SUSPECTED"


@dataclass(frozen=True)
class ClaimSettlementDecision:
    """Decisão final de liquidação do sinistro (Value Object)."""
    approved: bool
    status: ClaimStatus
    gross_loss: float
    deductible_applied: float
    payable_amount: float
    justification: str


@dataclass
class Claim:
    """Entidade do Domínio: Processo de Sinistro do Segurado."""
    claim_id: str
    policy_id: str
    insured_name: str
    occurrence_date: datetime
    claimed_amount: float
    description: str
    status: ClaimStatus = ClaimStatus.SUBMITTED
    assessment: Optional[DamageAssessment] = None
    settlement_decision: Optional[ClaimSettlementDecision] = None

    def attach_assessment(self, assessment: DamageAssessment) -> None:
        """Vincula laudo pericial ao sinistro."""
        if self.status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED]:
            raise InvalidClaimStateException("Não é possível alterar vistoria de sinistro já liquidado/encerrado.")
        self.assessment = assessment
        self.status = ClaimStatus.UNDER_REVIEW

    def apply_decision(self, decision: ClaimSettlementDecision) -> None:
        """Aplica a decisão final calculada pelo Domain Service."""
        self.settlement_decision = decision
        self.status = decision.status
