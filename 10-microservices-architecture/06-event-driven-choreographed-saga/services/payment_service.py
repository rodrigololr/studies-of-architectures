"""Payment Microservice na Saga Coreografada."""

import uuid
from typing import Dict, Any
from broker.event_broker import InMemoryEventBroker
from broker.domain_events import (
    OrderCreatedEvent,
    PaymentAuthorizedEvent,
    PaymentFailedEvent,
    InventoryFailedEvent,
    DeliveryFailedEvent,
    PaymentRefundedEvent,
)


class PaymentService:
    def __init__(self, broker: InMemoryEventBroker) -> None:
        self._broker = broker
        self._payments_db: Dict[str, Dict[str, Any]] = {}
        self._credit_limits: Dict[str, float] = {
            "CUST-ALICE": 10000.0,
            "CUST-BOB": 30.0,
            "CUST-CAROL": 10000.0,
            "CUST-DANIEL": 10000.0,
        }

        # Assinaturas da Coreografia
        self._broker.subscribe(OrderCreatedEvent, self._on_order_created)
        self._broker.subscribe(InventoryFailedEvent, self._on_downstream_failure)
        self._broker.subscribe(DeliveryFailedEvent, self._on_downstream_failure)

    def _on_order_created(self, event: OrderCreatedEvent) -> None:
        limit = self._credit_limits.get(event.customer_id, 0.0)
        if event.amount > limit:
            self._broker.publish(
                PaymentFailedEvent(
                    event_type="PAYMENT_FAILED",
                    order_id=event.order_id,
                    reason=f"Limite insuficiente (Disponível: R$ {limit:.2f})",
                )
            )
            return

        pay_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        self._payments_db[event.order_id] = {
            "payment_id": pay_id,
            "amount": event.amount,
            "customer_id": event.customer_id,
            "status": "AUTHORIZED",
        }
        self._credit_limits[event.customer_id] -= event.amount

        # Propaga o próximo passo da coreografia
        self._broker.publish(
            PaymentAuthorizedEvent(
                event_type="PAYMENT_AUTHORIZED",
                order_id=event.order_id,
                payment_id=pay_id,
                customer_id=event.customer_id,
                amount=event.amount,
                items=event.items,
                shipping_postal_code=event.shipping_postal_code,
            )
        )

    def _on_downstream_failure(self, event: Any) -> None:
        # Ação Compensatória reativa: estorna o pagamento
        if event.order_id in self._payments_db:
            pay_record = self._payments_db[event.order_id]
            if pay_record["status"] == "AUTHORIZED":
                pay_record["status"] = "REFUNDED"
                self._credit_limits[pay_record["customer_id"]] += pay_record["amount"]
                self._broker.publish(
                    PaymentRefundedEvent(
                        event_type="PAYMENT_REFUNDED",
                        order_id=event.order_id,
                        payment_id=pay_record["payment_id"],
                        reason=event.reason,
                    )
                )
