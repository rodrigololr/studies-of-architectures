"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de clientes (HTTP REST ou CLI), extrai parâmetros,
invoca a Camada de Serviço e formata a resposta padronizada,
capturando exceções de negócio e convertendo para status codes apropriados.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import OrderService
from business.exceptions import BusinessException, OrderNotFoundException


class OrderController:
    def __init__(self, service: OrderService) -> None:
        self.service = service

    def checkout(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Simula endpoint POST /api/orders/checkout"""
        try:
            customer_id = request_body.get("customer_id", "")
            items = request_body.get("items", [])
            coupon = request_body.get("coupon_code")

            order = self.service.create_order(
                customer_id=customer_id,
                items_data=items,
                coupon_code=coupon,
            )

            return {
                "status_code": 201,
                "data": {
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "subtotal": round(sum(i.subtotal for i in order.items), 2),
                    "freight": order.freight_value,
                    "discount": order.discount_value,
                    "total": order.total_amount,
                    "status": order.status.value,
                },
            }
        except BusinessException as ex:
            return {
                "status_code": 400,
                "error": str(ex),
            }

    def pay_order(self, order_id: str) -> Dict[str, Any]:
        """Simula endpoint PATCH /api/orders/{id}/pay"""
        try:
            order = self.service.mark_as_paid(order_id)
            return {
                "status_code": 200,
                "data": {"order_id": order.order_id, "status": order.status.value},
            }
        except OrderNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}
