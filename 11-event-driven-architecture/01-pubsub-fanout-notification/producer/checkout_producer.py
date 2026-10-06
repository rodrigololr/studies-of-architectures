"""Checkout Producer: Serviço de checkout que emite OrderPlacedEvent no broker."""

from typing import Tuple
from broker.pubsub_broker import PubSubBroker
from events.order_events import OrderItem, OrderPlacedEvent


class CheckoutService:
    """Produtor de eventos de checkout totalmente desacoplado dos canais de notificação."""

    def __init__(self, broker: PubSubBroker) -> None:
        self._broker = broker

    def complete_order(
        self,
        order_id: str,
        customer_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        items: Tuple[OrderItem, ...],
    ) -> OrderPlacedEvent:
        total_amount = sum(item.quantity * item.unit_price for item in items)
        event = OrderPlacedEvent(
            order_id=order_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            items=items,
            total_amount=total_amount,
        )

        # Publica no tópico de pedidos. O produtor não sabe quem irá consumir.
        self._broker.publish("orders.v1", event)
        return event
