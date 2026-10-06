"""
http_payment_controller.py - Adaptador Primário / Driver Adapter HTTP REST.

Simula a camada de entrada de um endpoint HTTP (ex: POST /api/v1/payments).
Traduz JSON bruto em entidade do domínio e invoca a porta `ProcessPaymentUseCasePort`.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
import json
from domain.models import PaymentRequest
from domain.exceptions import DomainException
from ports.driver import ProcessPaymentUseCasePort


class HttpPaymentController:
    def __init__(self, use_case: ProcessPaymentUseCasePort) -> None:
        self.use_case = use_case

    def handle_post_charge(self, http_payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Simula recepção de JSON no controller web."""
        try:
            payment_request = PaymentRequest(
                payment_id=http_payload.get("order_id", ""),
                amount=float(http_payload.get("amount", 0.0)),
                currency=http_payload.get("currency", "BRL"),
                customer_email=http_payload.get("email", ""),
                credit_card_token=http_payload.get("card_token", ""),
            )

            response = self.use_case.execute(payment_request)

            return 200, {
                "success": True,
                "data": {
                    "payment_id": response.payment_id,
                    "status": response.status.value,
                    "transaction_id": response.transaction_id,
                    "provider": response.provider_used,
                    "amount": response.amount,
                    "currency": response.currency,
                    "timestamp": response.processed_at.isoformat(),
                },
            }

        except DomainException as dom_err:
            return 422, {
                "success": False,
                "error": {
                    "type": dom_err.__class__.__name__,
                    "message": str(dom_err),
                },
            }
        except Exception as ex:
            return 500, {
                "success": False,
                "error": {
                    "type": "InternalServerError",
                    "message": str(ex),
                },
            }
