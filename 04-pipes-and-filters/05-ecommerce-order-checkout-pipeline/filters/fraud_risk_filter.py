"""
fraud_risk_filter.py - Filtro 2: Análise de Risco Antifraude.

Calcula score de risco com base em e-mails temporários e pedidos de valor atípico.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import OrderCheckoutContext


class FraudRiskFilter(Filter[OrderCheckoutContext, OrderCheckoutContext]):
    SUSPICIOUS_DOMAINS = {"tempmail.com", "disposable.com", "fakeinbox.org"}

    def process(self, ctx: OrderCheckoutContext) -> Optional[OrderCheckoutContext]:
        if not ctx.is_approved:
            return ctx

        domain = ctx.customer_email.split("@")[-1].lower() if "@" in ctx.customer_email else ""
        if domain in self.SUSPICIOUS_DOMAINS:
            ctx.is_approved = False
            ctx.rejection_stage = "FRAUD_RISK"
            ctx.rejection_reason = f"E-mail suspeito ou descartável detectado (@{domain})."
            return ctx

        # Pedidos com valores muito elevados (> R$ 10.000) requerem análise manual prévia
        if ctx.subtotal > 10000.0:
            ctx.is_approved = False
            ctx.rejection_stage = "FRAUD_RISK"
            ctx.rejection_reason = f"Valor do pedido (R$ {ctx.subtotal:,.2f}) excede o limite máximo permitido sem biometria."
            return ctx

        ctx.risk_score = 15  # Score baixo / seguro
        return ctx
