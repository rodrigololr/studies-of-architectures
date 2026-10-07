from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class CartCreated(DomainEvent):
    customer_id: str = ""

@dataclass(frozen=True)
class ItemAdded(DomainEvent):
    product_id: str = ""
    product_name: str = ""
    unit_price: float = 0.0
    quantity: int = 1

@dataclass(frozen=True)
class ItemRemoved(DomainEvent):
    product_id: str = ""

@dataclass(frozen=True)
class ItemQuantityUpdated(DomainEvent):
    product_id: str = ""
    new_quantity: int = 1

@dataclass(frozen=True)
class CouponApplied(DomainEvent):
    coupon_code: str = ""
    discount_percentage: float = 0.0

@dataclass(frozen=True)
class CartCheckedOut(DomainEvent):
    total_amount: float = 0.0
    payment_method: str = "CREDIT_CARD"

@dataclass(frozen=True)
class CartAbandoned(DomainEvent):
    abandon_reason: str = "SESSION_TIMEOUT"
