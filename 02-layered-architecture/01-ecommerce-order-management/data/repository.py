"""
repository.py - Camada de Dados (Data Layer).
Responsável pela persistência e recuperação de pedidos.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from data.models import OrderModel


class OrderRepository:
    def __init__(self) -> None:
        # Simula o armazenamento físico em tabela relacional
        self._table: Dict[str, OrderModel] = {}

    def save(self, order: OrderModel) -> OrderModel:
        self._table[order.order_id] = order
        return order

    def find_by_id(self, order_id: str) -> Optional[OrderModel]:
        return self._table.get(order_id)

    def list_by_customer(self, customer_id: str) -> List[OrderModel]:
        return [o for o in self._table.values() if o.customer_id == customer_id]
