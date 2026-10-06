"""
models.py - Camada de Dados (Data Layer).
Modelos de estoque físico de armazém e registro histórico de movimentações.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class MovementType(str, Enum):
    INBOUND = "INBOUND"     # Entrada de fornecedor
    RESERVE = "RESERVE"     # Bloqueio temporário para pedido em checkout
    DISPATCH = "DISPATCH"   # Saída física definitiva da doca
    ADJUSTMENT = "ADJUSTMENT"


@dataclass
class ProductStockModel:
    product_id: str
    sku: str
    product_name: str
    available_qty: int
    reserved_qty: int
    reorder_point: int  # Limiar de reposição emergencial

    @property
    def total_physical_qty(self) -> int:
        return self.available_qty + self.reserved_qty


@dataclass(frozen=True)
class StockMovementModel:
    movement_id: str
    product_id: str
    movement_type: MovementType
    quantity: int
    balance_after: int
    reason: str
    timestamp: str
