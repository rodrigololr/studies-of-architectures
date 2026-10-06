"""Order Microservice na Saga Coreografada."""

from typing import Dict, Any, Tuple
from broker.event_broker import InMemoryEventBroker
from broker.domain_events import (
    OrderCreatedEvent,
    DeliveryScheduledEvent,
    PaymentFailedEvent,
    InventoryFailedEvent,
    DeliveryFailedEvent,
)


class OrderService:
    def __init__(self, broker: InMemoryEventBroker) -> None:
        self._broker = broker
        self._orders_db: Dict[str, Dict[str, Any]] = {}

        # Assinatura de eventos para avanço e compensação
        self._broker.subscribe(DeliveryScheduledEvent, self._on_delivery_scheduled)
        self._broker.subscribe(PaymentFailedEvent, self._on_failure)
        self._broker.subscribe(InventoryFailedEvent, self._on_failure)
        self._broker.subscribe(DeliveryFailedEvent, self._on_failure)

    def place_order(
        self,
        order_id: str,
        customer_id: str,
        amount: float,
        items: Tuple[Tuple[str, int], ...],
        shipping_postal_code: str,
    ) -> None:
        self._orders_db[order_id] = {
            "order_id": order_id,
            "customer_id": customer_id,
            "status": "PENDING",
            "cancel_reason": None,
        }
        # Dispara o evento de início da coreografia
        self._broker.publish(
            OrderCreatedEvent(
                event_type="ORDER_CREATED",
                order_id=order_id,
                customer_id=customer_id,
                amount=amount,
                items=items,
                shipping_postal_code=shipping_postal_code,
            )
        )

    def _on_delivery_scheduled(self, event: DeliveryScheduledEvent) -> None:
        if event.order_id in self._orders_db:
            self._orders_db[event.order_id]["status"] = "CONFIRMED"

    def _on_failure(self, event: Any) -> None:
        if event.order_id in self._orders_db:
            self._orders_db[event.order_id]["status"] = "CANCELLED"
            self._orders_db[event.order_id]["cancel_reason"] = event.reason

    def get_order_status(self, order_id: str) -> str:
        return self._orders_db.get(order_id, {}).get("status", "NOT_FOUND")
