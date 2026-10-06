"""Ponto de Entrada e Facade do Módulo Warehousing."""

from typing import Optional
from shared.events import InProcessEventBus
from modules.procurement.public_contracts import PurchaseOrderReceivedDomainEvent
from modules.warehousing.public_contracts import (
    IWarehousingModule,
    WarehouseStockDto,
)
from modules.warehousing.internal.warehousing_internal import _InternalWarehousingRepository


class WarehousingModule(IWarehousingModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalWarehousingRepository()

        # Reage ao recebimento de mercadorias para atualizar prateleiras
        self._bus.subscribe(PurchaseOrderReceivedDomainEvent, self._handle_order_received)

    def _handle_order_received(self, e: PurchaseOrderReceivedDomainEvent) -> None:
        if not e.items:
            return
        for idx, item in enumerate(e.items, start=1):
            aisle = f"CORREDOR-{chr(64 + idx)}-01"
            self._repo.add(item.item_code, aisle, item.quantity)

    def get_stock(self, item_code: str) -> Optional[WarehouseStockDto]:
        st = self._repo.get(item_code)
        if not st:
            return None
        return WarehouseStockDto(
            item_code=st.item_code,
            aisle_location=st.aisle,
            available_quantity=st.quantity,
        )

    def pick_and_pack(self, item_code: str, quantity: int) -> bool:
        return self._repo.deduct(item_code, quantity)
