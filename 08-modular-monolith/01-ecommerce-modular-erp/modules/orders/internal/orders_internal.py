"""Implementação Interna Privada do Módulo Orders."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class _InternalOrderItem:
    sku: str
    product_name: str
    unit_price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity


@dataclass
class _InternalOrder:
    order_id: str
    customer_name: str
    customer_email: str
    items: List[_InternalOrderItem]
    status: str  # "PENDING_PAYMENT", "PAID", "CANCELLED", "STOCK_REJECTED"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)


class _InternalOrderRepository:
    """Repositório privado com persistência em memória do schema 'orders'."""
    def __init__(self) -> None:
        self._orders: Dict[str, _InternalOrder] = {}

    def save(self, order: _InternalOrder) -> None:
        self._orders[order.order_id] = order

    def find_by_id(self, order_id: str) -> Optional[_InternalOrder]:
        return self._orders.get(order_id)

    def list_all(self) -> List[_InternalOrder]:
        return list(self._orders.values())
