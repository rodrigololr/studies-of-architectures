"""Domain Events para Saga Coreografada em Microsserviços."""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    order_id: str


# Eventos de Ação Direta (Forward Events)
@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    customer_id: str = ""
    amount: float = 0.0
    items: Tuple[Tuple[str, int], ...] = ()
    shipping_postal_code: str = ""


@dataclass(frozen=True)
class PaymentAuthorizedEvent(DomainEvent):
    payment_id: str = ""
    customer_id: str = ""
    amount: float = 0.0
    items: Tuple[Tuple[str, int], ...] = ()
    shipping_postal_code: str = ""


@dataclass(frozen=True)
class InventoryReservedEvent(DomainEvent):
    reservation_id: str = ""
    payment_id: str = ""
    shipping_postal_code: str = ""


@dataclass(frozen=True)
class DeliveryScheduledEvent(DomainEvent):
    dispatch_id: str = ""


# Eventos de Falha e Compensação (Failure & Compensation Events)
@dataclass(frozen=True)
class PaymentFailedEvent(DomainEvent):
    reason: str = ""


@dataclass(frozen=True)
class InventoryFailedEvent(DomainEvent):
    payment_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class DeliveryFailedEvent(DomainEvent):
    reservation_id: str = ""
    payment_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class PaymentRefundedEvent(DomainEvent):
    payment_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class InventoryReleasedEvent(DomainEvent):
    reservation_id: str = ""
    reason: str = ""
