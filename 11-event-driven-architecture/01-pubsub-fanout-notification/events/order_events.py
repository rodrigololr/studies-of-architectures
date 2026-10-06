"""Domain Events for E-Commerce Order Lifecycle."""

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: float


@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    items: Tuple[OrderItem, ...]
    total_amount: float
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    occurred_at: float = field(default_factory=time.time)
