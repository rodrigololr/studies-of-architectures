"""Saga Models and State Enums."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class OrderStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class SagaStep(Enum):
    CREATE_ORDER = "CREATE_ORDER"
    PROCESS_PAYMENT = "PROCESS_PAYMENT"
    RESERVE_INVENTORY = "RESERVE_INVENTORY"
    SCHEDULE_DELIVERY = "SCHEDULE_DELIVERY"


class SagaStatus(Enum):
    SUCCESS = "SUCCESS"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float


@dataclass(frozen=True)
class OrderDetails:
    order_id: str
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_postal_code: str


@dataclass(frozen=True)
class SagaExecutionLog:
    step: SagaStep
    action: str  # "FORWARD" ou "COMPENSATION"
    status: str  # "SUCCESS", "FAILURE"
    details: str


@dataclass(frozen=True)
class SagaResult:
    saga_id: str
    order_id: str
    final_status: SagaStatus
    history: List[SagaExecutionLog]
    failure_reason: Optional[str] = None
