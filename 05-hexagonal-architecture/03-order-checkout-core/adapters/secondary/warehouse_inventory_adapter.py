"""
warehouse_inventory_adapter.py - Adaptador Secundário de Almoxarifado / Estoque.
"""

from __future__ import annotations
from typing import Dict, List
from domain.models import OrderItem
from ports.driven import InventoryReservationPort


class WarehouseInventoryAdapter(InventoryReservationPort):
    def __init__(self, initial_stock: Dict[str, int]) -> None:
        self._stock: Dict[str, int] = dict(initial_stock)
        self._reserved_per_order: Dict[str, List[OrderItem]] = {}

    def get_available(self, sku: str) -> int:
        return self._stock.get(sku, 0)

    def reserve_stock(self, order_id: str, items: List[OrderItem]) -> bool:
        # Verifica se todos os itens têm saldo disponível
        for item in items:
            if self._stock.get(item.sku, 0) < item.quantity:
                return False

        # Deduz saldo e guarda a reserva
        for item in items:
            self._stock[item.sku] -= item.quantity
        self._reserved_per_order[order_id] = list(items)
        return True

    def release_stock(self, order_id: str, items: List[OrderItem]) -> None:
        # Libera itens previamente bloqueados (compensação)
        if order_id in self._reserved_per_order:
            for item in self._reserved_per_order.pop(order_id):
                self._stock[item.sku] = self._stock.get(item.sku, 0) + item.quantity
