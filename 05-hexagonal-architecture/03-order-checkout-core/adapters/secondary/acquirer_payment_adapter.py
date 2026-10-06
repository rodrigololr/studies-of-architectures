"""
acquirer_payment_adapter.py - Adaptador Secundário de Gateway de Pagamento.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.models import CustomerInfo, PaymentConfirmation
from domain.exceptions import PaymentAuthorizationException
from ports.driven import PaymentGatewayPort


class CieloPaymentAdapter(PaymentGatewayPort):
    def charge(
        self,
        order_id: str,
        amount: float,
        customer: CustomerInfo,
        card_token: str,
    ) -> PaymentConfirmation:
        # Simula recusa de cartão com token inválido
        if card_token == "tok_declined_insufficient_funds":
            raise PaymentAuthorizationException("Cartão recusado pelo emissor: Saldo insuficiente.")

        if card_token == "tok_stolen_card":
            raise PaymentAuthorizationException("Cartão bloqueado por suspeita de fraude.")

        # Aprovação padrão
        auth_code = f"AUTH_{uuid.uuid4().hex[:8].upper()}"
        return PaymentConfirmation(
            authorization_code=auth_code,
            amount_paid=amount,
            paid_at=datetime.now(timezone.utc),
        )
