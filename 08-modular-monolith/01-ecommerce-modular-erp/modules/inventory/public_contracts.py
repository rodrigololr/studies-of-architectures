"""Contrato Público do Módulo Inventory (Public API / Facade Contract)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ReserveStockItem:
    """Item solicitado para reserva."""
    sku: str
    quantity: int


@dataclass(frozen=True)
class StockReservationResultDto:
    """Resultado da tentativa de reserva de estoque."""
    is_success: bool
    order_id: str
    missing_sku: Optional[str] = None
    message: str = ""


class IInventoryModule(ABC):
    """Interface pública exposta pelo Módulo de Estoque."""
    @abstractmethod
    def check_availability(self, sku: str) -> int:
        """Retorna o saldo físico disponível para venda."""
        pass

    @abstractmethod
    def reserve_stock(self, order_id: str, items: List[ReserveStockItem]) -> StockReservationResultDto:
        """Bloqueia unidades para o pedido. Lógica atômica por pedido."""
        pass

    @abstractmethod
    def release_stock(self, order_id: str) -> None:
        """Devolve ao estoque disponível unidades que haviam sido reservadas."""
        pass

    @abstractmethod
    def commit_stock(self, order_id: str) -> None:
        """Baixa definitiva do estoque reservado após confirmação de pagamento."""
        pass
