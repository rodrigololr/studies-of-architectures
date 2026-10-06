"""Email Notification Consumer: Consumidor Fan-out de recibos por e-mail."""

from typing import List, Dict, Any
from events.order_events import OrderPlacedEvent


class EmailNotificationConsumer:
    def __init__(self) -> None:
        self.sent_emails: List[Dict[str, Any]] = []

    def handle(self, event: OrderPlacedEvent) -> None:
        items_summary = ", ".join(f"{item.quantity}x {item.product_name}" for item in event.items)
        subject = f"Confirmação do Pedido #{event.order_id}"
        body = (
            f"Olá {event.customer_name}, seu pedido foi recebido com sucesso!\n"
            f"Itens: {items_summary}\n"
            f"Total: R$ {event.total_amount:,.2f}"
        )
        self.sent_emails.append({
            "to": event.customer_email,
            "subject": subject,
            "body": body,
            "order_id": event.order_id,
        })
