"""
stripe_adapter.py - Adaptador Secundário / Driven Adapter para Stripe.

Implementa `PaymentGatewayPort`. Traduz requisições do domínio para a
comunicação simulada com o SDK/API REST da Stripe.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.models import PaymentRequest, PaymentResponse, PaymentStatus
from ports.driven import PaymentGatewayPort


class StripePaymentAdapter(PaymentGatewayPort):
    def __init__(self, api_key: str, is_active: bool = True) -> None:
        self._api_key = api_key
        self._is_active = is_active

    @property
    def provider_name(self) -> str:
        return "Stripe Inc. (v3-api)"

    @property
    def is_available(self) -> bool:
        return self._is_active

    def set_availability(self, status: bool) -> None:
        """Permite simular oscilação de rede ou manutenção do parceiro."""
        self._is_active = status

    def charge(self, request: PaymentRequest) -> PaymentResponse:
        # Simula validação do token / gateway Stripe
        if not self._is_active:
            return PaymentResponse(
                payment_id=request.payment_id,
                amount=request.amount,
                currency=request.currency,
                status=PaymentStatus.FAILED,
                provider_used=self.provider_name,
                processed_at=datetime.now(timezone.utc),
                error_message="Stripe API Gateway Timeout (504)",
            )

        # Regra de simulação: valores acima de 50000 exigem aprovação manual no Stripe
        if request.amount > 50_000:
            return PaymentResponse(
                payment_id=request.payment_id,
                amount=request.amount,
                currency=request.currency,
                status=PaymentStatus.FAILED,
                provider_used=self.provider_name,
                processed_at=datetime.now(timezone.utc),
                error_message="Stripe Risk Engine: Charge exceeds auto-capture threshold",
            )

        # Transação autorizada com sucesso
        transaction_id = f"ch_stripe_{uuid.uuid4().hex[:12]}"
        return PaymentResponse(
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.AUTHORIZED,
            transaction_id=transaction_id,
            provider_used=self.provider_name,
            processed_at=datetime.now(timezone.utc),
        )
