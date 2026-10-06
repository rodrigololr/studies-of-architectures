"""
sql_order_repository_adapter.py - Adaptador Secundário de Repositório de Pedidos.
"""

from __future__ import annotations
from typing import Dict, Optional
from domain.models import Order
from ports.driven import OrderRepositoryPort


class InMemoryOrderRepositoryAdapter(OrderRepositoryPort):
    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._orders[order.order_id] = order

    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
