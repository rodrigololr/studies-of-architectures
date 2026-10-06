"""Implementação Interna do Módulo Warehousing (Schema: warehousing)."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class _InternalStorageItem:
    item_code: str
    aisle: str
    quantity: int


class _InternalWarehousingRepository:
    def __init__(self) -> None:
        self._stocks: Dict[str, _InternalStorageItem] = {}

    def get(self, item_code: str) -> Optional[_InternalStorageItem]:
        return self._stocks.get(item_code)

    def add(self, item_code: str, aisle: str, qty: int) -> None:
        if item_code in self._stocks:
            self._stocks[item_code].quantity += qty
        else:
            self._stocks[item_code] = _InternalStorageItem(item_code=item_code, aisle=aisle, quantity=qty)

    def deduct(self, item_code: str, qty: int) -> bool:
        item = self._stocks.get(item_code)
        if not item or item.quantity < qty:
            return False
        item.quantity -= qty
        return True
