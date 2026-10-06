"""OrderService instrumentado com Distributed Tracing."""

import time
from typing import Dict, Any
from tracing.tracer import Tracer
from services.payment_service import PaymentService


class OrderService:
    def __init__(self, tracer: Tracer, payment_svc: PaymentService) -> None:
        self._tracer = tracer
        self._payment = payment_svc

    def create_order(
        self, headers: Dict[str, str], order_id: str, customer_id: str, amount: float
    ) -> Dict[str, Any]:
        with self._tracer.start_span("create_order_workflow", headers) as span:
            span.attributes["order.id"] = order_id
            span.attributes["order.customer_id"] = customer_id
            span.attributes["order.total_amount"] = amount
            time.sleep(0.01)

            # Prepara headers downstream para o pagamento
            downstream_headers: Dict[str, str] = {}
            self._tracer.inject_context(span, downstream_headers)

            payment_res = self._payment.process_payment(downstream_headers, order_id, amount)

            return {
                "order_id": order_id,
                "order_status": "CONFIRMED",
                "payment_details": payment_res,
            }
