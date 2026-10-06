"""
pagarme_adapter.py - Adaptador Secundário / Driven Adapter para Pagar.me.

Implementa `PaymentGatewayPort`.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.models import PaymentRequest, PaymentResponse, PaymentStatus
from ports.driven import PaymentGatewayPort


class PagarMePaymentAdapter(PaymentGatewayPort):
    def __init__(self, encryption_key: str, is_active: bool = True) -> None:
        self._encryption_key = encryption_key
        self._is_active = is_active

    @property
    def provider_name(self) -> str:
        return "Pagar.me Stone Co."

    @property
    def is_available(self) -> bool:
        return self._is_active

    def set_availability(self, status: bool) -> None:
        self._is_active = status

    def charge(self, request: PaymentRequest) -> PaymentResponse:
        if not self._is_active:
            return PaymentResponse(
                payment_id=request.payment_id,
                amount=request.amount,
                currency=request.currency,
                status=PaymentStatus.FAILED,
                provider_used=self.provider_name,
                processed_at=datetime.now(timezone.utc),
                error_message="Pagar.me Adquirer Connection Refused",
            )

        transaction_id = f"tid_pagarme_{uuid.uuid4().hex[:10]}"
        return PaymentResponse(
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.AUTHORIZED,
            transaction_id=transaction_id,
            provider_used=self.provider_name,
            processed_at=datetime.now(timezone.utc),
        )
