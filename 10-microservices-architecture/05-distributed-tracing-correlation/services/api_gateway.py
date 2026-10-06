"""ApiGatewayService: Origem do Root Span na borda da arquitetura."""

import time
from typing import Dict, Any, Tuple
from tracing.tracer import Tracer
from services.order_service import OrderService


class ApiGatewayService:
    def __init__(self, tracer: Tracer, order_svc: OrderService) -> None:
        self._tracer = tracer
        self._order = order_svc

    def handle_checkout_request(
        self, order_id: str, customer_id: str, amount: float
    ) -> Tuple[Dict[str, Any], str]:
        # Como o Gateway é a borda, ele inicia o Root Span (sem incoming_headers)
        with self._tracer.start_span("http_ingress_checkout") as root_span:
            root_span.attributes["http.method"] = "POST"
            root_span.attributes["http.target"] = "/api/v1/checkout"
            root_span.attributes["client.user_agent"] = "MobileApp/2.4.0"
            time.sleep(0.005)

            downstream_headers: Dict[str, str] = {}
            self._tracer.inject_context(root_span, downstream_headers)

            order_res = self._order.create_order(
                downstream_headers, order_id, customer_id, amount
            )

            return order_res, root_span.trace_id
