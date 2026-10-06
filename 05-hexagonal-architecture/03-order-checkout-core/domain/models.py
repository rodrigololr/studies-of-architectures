"""
models.py - Modelos de domínio do checkout de pedidos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FAILED_PAYMENT = "FAILED_PAYMENT"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    sku: str
    name: str
    unit_price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return round(self.unit_price * self.quantity, 2)


@dataclass(frozen=True)
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    postal_code: str


@dataclass(frozen=True)
class CheckoutCommand:
    order_id: str
    customer: CustomerInfo
    items: List[OrderItem]
    card_token: str


@dataclass(frozen=True)
class PaymentConfirmation:
    authorization_code: str
    amount_paid: float
    paid_at: datetime


@dataclass(frozen=True)
class InvoiceDetails:
    invoice_number: str
    fiscal_key: str
    issued_at: datetime


@dataclass
class Order:
    order_id: str
    customer: CustomerInfo
    items: List[OrderItem]
    items_total: float
    shipping_fee: float
    grand_total: float
    status: OrderStatus
    payment_info: Optional[PaymentConfirmation] = None
    invoice_info: Optional[InvoiceDetails] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class CheckoutResult:
    order_id: str
    status: OrderStatus
    items_total: float
    shipping_fee: float
    grand_total: float
    authorization_code: Optional[str] = None
    invoice_number: Optional[str] = None
    error_reason: Optional[str] = None
