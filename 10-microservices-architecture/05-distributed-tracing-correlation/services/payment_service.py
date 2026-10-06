"""PaymentService instrumentado com Distributed Tracing."""

import time
from typing import Dict, Any
from tracing.tracer import Tracer
from services.fraud_service import FraudDetectionService


class PaymentService:
    def __init__(self, tracer: Tracer, fraud_svc: FraudDetectionService) -> None:
        self._tracer = tracer
        self._fraud = fraud_svc

    def process_payment(self, headers: Dict[str, str], order_id: str, amount: float) -> Dict[str, Any]:
        with self._tracer.start_span("authorize_payment", headers) as span:
            span.attributes["payment.order_id"] = order_id
            span.attributes["payment.amount"] = amount
            span.attributes["payment.gateway"] = "Stripe-Mock"
            time.sleep(0.015)

            # Prepara headers downstream para o serviço de fraude
            downstream_headers: Dict[str, str] = {}
            self._tracer.inject_context(span, downstream_headers)

            fraud_result = self._fraud.evaluate_risk(downstream_headers, amount)

            return {
                "payment_status": "CAPTURED",
                "fraud_check": fraud_result,
            }
