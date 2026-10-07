from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class ProductCreated(DomainEvent):
    product_name: str = ""
    category: str = ""
    initial_price: float = 0.0

@dataclass(frozen=True)
class PriceChanged(DomainEvent):
    old_price: float = 0.0
    new_price: float = 0.0
    reason: str = ""

@dataclass(frozen=True)
class ProductPurchased(DomainEvent):
    order_id: str = ""
    unit_price: float = 0.0
    quantity: int = 1

@dataclass(frozen=True)
class ProductReturned(DomainEvent):
    order_id: str = ""
    quantity: int = 1
    refund_amount: float = 0.0
    return_reason: str = ""
