"""SMS Notification Consumer: Consumidor Fan-out de alertas rápidos por SMS."""

from typing import List, Dict, Any
from events.order_events import OrderPlacedEvent


class SmsNotificationConsumer:
    def __init__(self) -> None:
        self.sent_sms: List[Dict[str, Any]] = []

    def handle(self, event: OrderPlacedEvent) -> None:
        msg = f"Loja: Pedido #{event.order_id} de R$ {event.total_amount:.2f} aprovado. Acompanhe a entrega pelo app!"
        self.sent_sms.append({
            "phone": event.customer_phone,
            "message": msg[:140],
            "order_id": event.order_id,
        })
