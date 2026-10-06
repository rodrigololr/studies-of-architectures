"""Delivery Microservice na Saga Coreografada."""

import uuid
from typing import Dict, Any
from broker.event_broker import InMemoryEventBroker
from broker.domain_events import (
    InventoryReservedEvent,
    DeliveryScheduledEvent,
    DeliveryFailedEvent,
)


class DeliveryService:
    def __init__(self, broker: InMemoryEventBroker) -> None:
        self._broker = broker
        self._dispatches: Dict[str, Dict[str, Any]] = {}
        self._blocked_postcodes = {"99999-999"}

        # Assinatura de evento de avanço
        self._broker.subscribe(InventoryReservedEvent, self._on_inventory_reserved)

    def _on_inventory_reserved(self, event: InventoryReservedEvent) -> None:
        if event.shipping_postal_code in self._blocked_postcodes:
            # Falha logística -> dispara evento de falha que desencadeia as compensações nos outros serviços
            self._broker.publish(
                DeliveryFailedEvent(
                    event_type="DELIVERY_FAILED",
                    order_id=event.order_id,
                    reservation_id=event.reservation_id,
                    payment_id=event.payment_id,
                    reason=f"Área com restrição de entrega (CEP: {event.shipping_postal_code})",
                )
            )
            return

        dispatch_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        self._dispatches[event.order_id] = {
            "dispatch_id": dispatch_id,
            "status": "SCHEDULED",
        }

        # Conclusão da coreografia com sucesso
        self._broker.publish(
            DeliveryScheduledEvent(
                event_type="DELIVERY_SCHEDULED",
                order_id=event.order_id,
                dispatch_id=dispatch_id,
            )
        )
