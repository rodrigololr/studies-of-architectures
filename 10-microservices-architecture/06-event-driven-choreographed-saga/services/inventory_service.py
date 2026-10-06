"""Inventory Microservice na Saga Coreografada."""

import uuid
from typing import Dict, Any
from broker.event_broker import InMemoryEventBroker
from broker.domain_events import (
    PaymentAuthorizedEvent,
    InventoryReservedEvent,
    InventoryFailedEvent,
    DeliveryFailedEvent,
    InventoryReleasedEvent,
)


class InventoryService:
    def __init__(self, broker: InMemoryEventBroker) -> None:
        self._broker = broker
        self._stock_db: Dict[str, int] = {
            "SKU-TV-OLED": 5,
            "SKU-IPHONE": 10,
            "SKU-CONSOLE": 0,  # Sem estoque
        }
        self._reservations: Dict[str, Dict[str, Any]] = {}

        # Assinaturas da Coreografia
        self._broker.subscribe(PaymentAuthorizedEvent, self._on_payment_authorized)
        self._broker.subscribe(DeliveryFailedEvent, self._on_delivery_failed)

    def _on_payment_authorized(self, event: PaymentAuthorizedEvent) -> None:
        # 1. Verifica se todos os itens possuem estoque
        for sku, qty in event.items:
            current_stock = self._stock_db.get(sku, 0)
            if current_stock < qty:
                self._broker.publish(
                    InventoryFailedEvent(
                        event_type="INVENTORY_FAILED",
                        order_id=event.order_id,
                        payment_id=event.payment_id,
                        reason=f"Estoque esgotado para o SKU {sku}",
                    )
                )
                return

        # 2. Reserva o estoque
        resv_id = f"RESV-{uuid.uuid4().hex[:8].upper()}"
        reserved_list = []
        for sku, qty in event.items:
            self._stock_db[sku] -= qty
            reserved_list.append((sku, qty))

        self._reservations[event.order_id] = {
            "resv_id": resv_id,
            "items": reserved_list,
            "status": "RESERVED",
        }

        # Avança a coreografia emitindo evento
        self._broker.publish(
            InventoryReservedEvent(
                event_type="INVENTORY_RESERVED",
                order_id=event.order_id,
                reservation_id=resv_id,
                payment_id=event.payment_id,
                shipping_postal_code=event.shipping_postal_code,
            )
        )

    def _on_delivery_failed(self, event: DeliveryFailedEvent) -> None:
        # Ação Compensatória: Libera estoque reservado
        if event.order_id in self._reservations:
            resv = self._reservations[event.order_id]
            if resv["status"] == "RESERVED":
                for sku, qty in resv["items"]:
                    self._stock_db[sku] += qty
                resv["status"] = "RELEASED"
                self._broker.publish(
                    InventoryReleasedEvent(
                        event_type="INVENTORY_RELEASED",
                        order_id=event.order_id,
                        reservation_id=resv["resv_id"],
                        reason=event.reason,
                    )
                )

    def get_stock(self, sku: str) -> int:
        return self._stock_db.get(sku, 0)
