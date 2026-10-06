"""
mercadopago_adapter.py - Adaptador Secundário / Driven Adapter para Mercado Pago.

Implementa `PaymentGatewayPort`.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.models import PaymentRequest, PaymentResponse, PaymentStatus
from ports.driven import PaymentGatewayPort


class MercadoPagoPaymentAdapter(PaymentGatewayPort):
    def __init__(self, access_token: str, is_active: bool = True) -> None:
        self._access_token = access_token
        self._is_active = is_active

    @property
    def provider_name(self) -> str:
        return "Mercado Pago Gateway"

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
                error_message="Mercado Pago Service Unavailable",
            )

        transaction_id = f"mp_pay_{uuid.uuid4().hex[:10]}"
        return PaymentResponse(
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.AUTHORIZED,
            transaction_id=transaction_id,
            provider_used=self.provider_name,
            processed_at=datetime.now(timezone.utc),
        )
