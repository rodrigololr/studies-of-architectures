"""
repository.py - Camada de Dados (Data Layer).
Acesso ao catálogo de estoque de armazém e trilha de movimentações.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from data.models import ProductStockModel, StockMovementModel


class InventoryRepository:
    def __init__(self) -> None:
        self._table: Dict[str, ProductStockModel] = {}

    def save(self, stock: ProductStockModel) -> ProductStockModel:
        self._table[stock.product_id] = stock
        return stock

    def find_by_id(self, product_id: str) -> Optional[ProductStockModel]:
        return self._table.get(product_id)

    def find_by_sku(self, sku: str) -> Optional[ProductStockModel]:
        normalized = sku.strip().upper()
        for s in self._table.values():
            if s.sku.strip().upper() == normalized:
                return s
        return None


class StockMovementRepository:
    def __init__(self) -> None:
        self._movements: List[StockMovementModel] = []

    def record(self, movement: StockMovementModel) -> StockMovementModel:
        self._movements.append(movement)
        return movement

    def list_by_product(self, product_id: str) -> List[StockMovementModel]:
        return [m for m in self._movements if m.product_id == product_id]
