"""Contrato Público do Módulo Warehousing (Armazenagem e Centros de Distribuição)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WarehouseStockDto:
    item_code: str
    aisle_location: str
    available_quantity: int


class IWarehousingModule(ABC):
    @abstractmethod
    def get_stock(self, item_code: str) -> Optional[WarehouseStockDto]:
        pass

    @abstractmethod
    def pick_and_pack(self, item_code: str, quantity: int) -> bool:
        """Separa e embala unidades para expedição."""
        pass
