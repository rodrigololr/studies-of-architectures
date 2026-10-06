"""Ponto de Entrada e Facade do Módulo Inventory."""

from typing import List
from shared.events import InProcessEventBus
from modules.inventory.public_contracts import (
    IInventoryModule,
    ReserveStockItem,
    StockReservationResultDto,
)
from modules.inventory.internal.inventory_internal import _InternalInventoryRepository


class InventoryModule(IInventoryModule):
    """Facade pública do módulo Inventory."""
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._repo = _InternalInventoryRepository()
        self._bus = event_bus

    def seed_stock(self, sku: str, quantity: int) -> None:
        """Carga inicial de saldo de estoque."""
        self._repo.set_stock(sku, quantity)

    def check_availability(self, sku: str) -> int:
        stock = self._repo.get_stock(sku)
        return stock.available_quantity if stock else 0

    def reserve_stock(self, order_id: str, items: List[ReserveStockItem]) -> StockReservationResultDto:
        """Reserva atômica de múltiplos itens no estoque."""
        # 1. Verifica se todos os itens possuem saldo antes de modificar qualquer um
        for item in items:
            stock = self._repo.get_stock(item.sku)
            if not stock or not stock.can_reserve(item.quantity):
                avail = stock.available_quantity if stock else 0
                return StockReservationResultDto(
                    is_success=False,
                    order_id=order_id,
                    missing_sku=item.sku,
                    message=f"Estoque insuficiente para SKU '{item.sku}'. Solicitado: {item.quantity}, Disponível: {avail}."
                )

        # 2. Efetua a reserva de todos os itens
        for item in items:
            stock = self._repo.get_stock(item.sku)
            if stock:
                stock.reserve(item.quantity)

        self._repo.store_reservation(order_id, items)
        return StockReservationResultDto(
            is_success=True,
            order_id=order_id,
            message="Estoque reservado com sucesso com garantia de bloqueio temporário."
        )

    def release_stock(self, order_id: str) -> None:
        """Libera itens reservados de volta para saldo disponível."""
        items = self._repo.pop_reservation(order_id)
        if not items:
            return
        for item in items:
            stock = self._repo.get_stock(item.sku)
            if stock:
                stock.release(item.quantity)

    def commit_stock(self, order_id: str) -> None:
        """Baixa permanente das unidades reservadas."""
        items = self._repo.pop_reservation(order_id)
        if not items:
            return
        for item in items:
            stock = self._repo.get_stock(item.sku)
            if stock:
                stock.commit(item.quantity)
