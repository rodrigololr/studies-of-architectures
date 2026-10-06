"""
fiscal_tax_filter.py - Filtro 4: Cálculo Tributário e Fiscal Interestadual.

Aplica alíquotas de ICMS de acordo com o estado de destino da entrega.
"""

from __future__ import annotations
from typing import Dict, Optional
from pipeline.base import Filter
from pipeline.context import OrderCheckoutContext


class FiscalTaxFilter(Filter[OrderCheckoutContext, OrderCheckoutContext]):
    # Tabela simplificada de alíquotas interestaduais
    TAX_RATES: Dict[str, float] = {
        "SP": 0.18,  # 18% ICMS interno
        "RJ": 0.20,  # 20% ICMS
        "MG": 0.18,
        "RS": 0.17,
        "PR": 0.19,
    }
    DEFAULT_TAX_RATE = 0.12  # 12% para outros estados

    def process(self, ctx: OrderCheckoutContext) -> Optional[OrderCheckoutContext]:
        if not ctx.is_approved:
            return ctx

        uf = ctx.destination_state.upper().strip()
        rate = self.TAX_RATES.get(uf, self.DEFAULT_TAX_RATE)

        tax = round(ctx.subtotal * rate, 2)
        ctx.tax_amount = tax
        ctx.final_total = round(ctx.subtotal + tax, 2)

        return ctx
