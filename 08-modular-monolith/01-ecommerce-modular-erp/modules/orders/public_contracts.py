"""Contrato Público do Módulo Orders."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class OrderItemInputDto:
    sku: str
    quantity: int


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_name: str
    customer_email: str
    items: List[OrderItemInputDto]
    payment_method: str  # "CREDIT_CARD", "PIX", etc.


@dataclass(frozen=True)
class OrderSummaryDto:
    order_id: str
    customer_name: str
    customer_email: str
    status: str  # "PENDING", "PAID", "CANCELLED", "FAILED_STOCK"
    total_amount: float
    items_count: int
    message: str = ""


@dataclass(frozen=True)
class OrderPlacedDomainEvent(DomainEvent):
    """Evento emitido quando uma ordem é criada."""
    order_id: str = ""
    customer_email: str = ""
    total_amount: float = 0.0


@dataclass(frozen=True)
class OrderCancelledDomainEvent(DomainEvent):
    """Evento emitido quando um pedido é cancelado por falta de pagamento ou desistência."""
    order_id: str = ""
    reason: str = ""


class IOrdersModule(ABC):
    """Interface pública exposta pelo Módulo de Pedidos."""
    @abstractmethod
    def place_order(self, cmd: PlaceOrderCommand) -> OrderSummaryDto:
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[OrderSummaryDto]:
        pass
