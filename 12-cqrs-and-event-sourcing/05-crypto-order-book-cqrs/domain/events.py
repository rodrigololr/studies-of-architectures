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
class OrderPlaced(DomainEvent):
    order_id: str = ""
    side: str = "BUY"  # BUY ou SELL
    price: float = 0.0
    quantity: float = 0.0

@dataclass(frozen=True)
class OrderMatched(DomainEvent):
    trade_id: str = ""
    maker_order_id: str = ""
    taker_order_id: str = ""
    match_price: float = 0.0
    executed_quantity: float = 0.0

@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: str = ""
    side: str = "BUY"
    price: float = 0.0
    unfilled_quantity: float = 0.0
    reason: str = "CLIENT_REQUEST"
