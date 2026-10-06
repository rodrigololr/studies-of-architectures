"""Implementação Interna Privada do Módulo Inventory."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from modules.inventory.public_contracts import ReserveStockItem


@dataclass
class _InternalStockItem:
    """Item em depósito com saldo físico e controle de reservas."""
    sku: str
    available_quantity: int
    reserved_quantity: int = 0

    def can_reserve(self, qty: int) -> bool:
        return self.available_quantity >= qty

    def reserve(self, qty: int) -> None:
        self.available_quantity -= qty
        self.reserved_quantity += qty

    def release(self, qty: int) -> None:
        self.reserved_quantity = max(0, self.reserved_quantity - qty)
        self.available_quantity += qty

    def commit(self, qty: int) -> None:
        self.reserved_quantity = max(0, self.reserved_quantity - qty)


class _InternalInventoryRepository:
    """Repositório privado com persistência em memória do schema 'inventory'."""
    def __init__(self) -> None:
        self._stocks: Dict[str, _InternalStockItem] = {}
        # Mapeamento de reservas por pedido: {order_id: [ReserveStockItem, ...]}
        self._reservations_by_order: Dict[str, List[ReserveStockItem]] = {}

    def get_stock(self, sku: str) -> Optional[_InternalStockItem]:
        return self._stocks.get(sku)

    def set_stock(self, sku: str, quantity: int) -> None:
        self._stocks[sku] = _InternalStockItem(sku=sku, available_quantity=quantity)

    def store_reservation(self, order_id: str, items: List[ReserveStockItem]) -> None:
        self._reservations_by_order[order_id] = items

    def pop_reservation(self, order_id: str) -> Optional[List[ReserveStockItem]]:
        return self._reservations_by_order.pop(order_id, None)

    def get_reservation(self, order_id: str) -> Optional[List[ReserveStockItem]]:
        return self._reservations_by_order.get(order_id)
