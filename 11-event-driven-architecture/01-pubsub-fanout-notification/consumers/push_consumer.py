"""Push Notification Consumer: Consumidor Fan-out de notificações para smartphone."""

from typing import List, Dict, Any
from events.order_events import OrderPlacedEvent


class PushNotificationConsumer:
    def __init__(self) -> None:
        self.sent_pushes: List[Dict[str, Any]] = []

    def handle(self, event: OrderPlacedEvent) -> None:
        self.sent_pushes.append({
            "target_user_id": event.customer_id,
            "title": "🎉 Pedido Confirmado!",
            "message": f"Preparamos o envio do pedido #{event.order_id}.",
            "badge_count": 1,
        })
