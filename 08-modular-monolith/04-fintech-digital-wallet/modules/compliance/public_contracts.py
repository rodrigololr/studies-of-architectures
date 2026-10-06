"""Contrato Público do Módulo Compliance (Prevenção à Lavagem de Dinheiro - PLD/BACEN)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ComplianceCheckRequestDto:
    origin_account_id: str
    origin_cpf: str
    destination_pix_key: str
    amount: float


@dataclass(frozen=True)
class ComplianceDecisionDto:
    is_approved: bool
    requires_manual_review: bool
    risk_score: float  # 0.0 a 1.0
    reason: str


class IComplianceModule(ABC):
    @abstractmethod
    def evaluate_transfer(self, req: ComplianceCheckRequestDto) -> ComplianceDecisionDto:
        pass

    @abstractmethod
    def blacklist_pix_key(self, pix_key: str) -> None:
        pass
