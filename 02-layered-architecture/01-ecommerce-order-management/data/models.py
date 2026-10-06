"""
models.py - Camada de Dados (Data Layer).
Modelos de dados representando as tabelas do banco de dados relacional.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItemModel:
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class OrderModel:
    order_id: str
    customer_id: str
    items: List[OrderItemModel]
    freight_value: float
    discount_value: float
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    coupon_code: Optional[str] = None
