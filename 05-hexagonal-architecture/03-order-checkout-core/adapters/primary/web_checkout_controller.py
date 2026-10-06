"""
web_checkout_controller.py - Adaptador Primário Web / E-commerce Controller.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from domain.models import CheckoutCommand, CustomerInfo, OrderItem
from domain.exceptions import CheckoutDomainException
from ports.driver import CheckoutUseCasePort, GetOrderStatusUseCasePort


class WebCheckoutController:
    def __init__(
        self,
        checkout_use_case: CheckoutUseCasePort,
        order_status_use_case: GetOrderStatusUseCasePort,
    ) -> None:
        self.checkout_use_case = checkout_use_case
        self.order_status_use_case = order_status_use_case

    def handle_post_checkout(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            cust_data = payload.get("customer", {})
            customer = CustomerInfo(
                customer_id=cust_data.get("id", ""),
                name=cust_data.get("name", ""),
                email=cust_data.get("email", ""),
                postal_code=cust_data.get("postal_code", ""),
            )

            items = [
                OrderItem(
                    sku=item["sku"],
                    name=item["name"],
                    unit_price=float(item["unit_price"]),
                    quantity=int(item["quantity"]),
                )
                for item in payload.get("items", [])
            ]

            cmd = CheckoutCommand(
                order_id=payload.get("order_id", ""),
                customer=customer,
                items=items,
                card_token=payload.get("card_token", ""),
            )

            res = self.checkout_use_case.execute_checkout(cmd)

            return 200, {
                "success": True,
                "order_id": res.order_id,
                "status": res.status.value,
                "items_total": res.items_total,
                "shipping_fee": res.shipping_fee,
                "grand_total": res.grand_total,
                "auth_code": res.authorization_code,
                "invoice_number": res.invoice_number,
            }

        except CheckoutDomainException as dom_err:
            return 400, {
                "success": False,
                "error": dom_err.__class__.__name__,
                "detail": str(dom_err),
            }
        except Exception as ex:
            return 500, {
                "success": False,
                "error": "InternalServerError",
                "detail": str(ex),
            }
