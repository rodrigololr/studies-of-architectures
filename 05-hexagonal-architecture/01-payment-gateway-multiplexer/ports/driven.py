"""
driven.py - Portas Secundárias / Outbound (Driven Ports).

Contratos abstratos do que o Core da aplicação necessita de serviços externos.
Adaptadores secundários (Stripe, Pagarme, Bancos de Dados) implementam estas portas.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import PaymentRequest, PaymentResponse


class PaymentGatewayPort(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome legível do provedor de pagamento."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Indica se o gateway está respondendo saudavelmente (Healthcheck)."""
        pass

    @abstractmethod
    def charge(self, request: PaymentRequest) -> PaymentResponse:
        """Executa a transação financeira na rede adquirente."""
        pass


class PaymentAuditRepositoryPort(ABC):
    @abstractmethod
    def save_audit(self, response: PaymentResponse) -> None:
        """Persiste o registro histórico auditável da transação autorizada."""
        pass

    @abstractmethod
    def list_history(self) -> List[PaymentResponse]:
        """Recupera o histórico de cobranças processadas."""
        pass
