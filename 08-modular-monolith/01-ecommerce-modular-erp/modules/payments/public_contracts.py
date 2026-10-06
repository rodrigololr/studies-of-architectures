"""Contrato Público do Módulo Payments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class ProcessPaymentCommand:
    """Comando para processamento de pagamento."""
    order_id: str
    customer_email: str
    amount: float
    payment_method: str  # "CREDIT_CARD", "PIX", "BOLETO"


@dataclass(frozen=True)
class PaymentResultDto:
    """Resultado retornado ao cliente/orquestrador."""
    transaction_id: str
    order_id: str
    is_successful: bool
    auth_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class PaymentSucceededDomainEvent(DomainEvent):
    """Evento emitido quando o pagamento é liquidado com sucesso."""
    order_id: str = ""
    transaction_id: str = ""
    amount: float = 0.0


@dataclass(frozen=True)
class PaymentFailedDomainEvent(DomainEvent):
    """Evento emitido quando o pagamento é recusado."""
    order_id: str = ""
    reason: str = ""


class IPaymentsModule(ABC):
    """Interface pública exposta pelo Módulo de Pagamentos."""
    @abstractmethod
    def process_payment(self, cmd: ProcessPaymentCommand) -> PaymentResultDto:
        pass
