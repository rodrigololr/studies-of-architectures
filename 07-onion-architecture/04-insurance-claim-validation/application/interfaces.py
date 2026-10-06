"""Contratos e interfaces abstratas do anel de aplicação (Onion Architecture)."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.model.policy import Policy
from domain.model.claim import Claim


class IPolicyRepository(ABC):
    """Porta/Interface de repositório de apólices."""
    @abstractmethod
    def get_by_id(self, policy_id: str) -> Optional[Policy]:
        pass

    @abstractmethod
    def save(self, policy: Policy) -> None:
        pass


class IClaimRepository(ABC):
    """Porta/Interface de repositório de sinistros."""
    @abstractmethod
    def get_by_id(self, claim_id: str) -> Optional[Claim]:
        pass

    @abstractmethod
    def save(self, claim: Claim) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[Claim]:
        pass


class IFraudDetectionGateway(ABC):
    """Porta/Interface para birô antifraude de seguros."""
    @abstractmethod
    def evaluate_risk(self, claim: Claim) -> float:
        """Retorna uma pontuação de risco entre 0.0 (seguro) e 1.0 (alto risco)."""
        pass


class INotificationGateway(ABC):
    """Porta/Interface para comunicação com o segurado."""
    @abstractmethod
    def notify_insured(self, insured_name: str, message: str) -> None:
        pass
