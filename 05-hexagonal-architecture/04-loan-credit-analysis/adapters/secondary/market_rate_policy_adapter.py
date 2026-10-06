"""
market_rate_policy_adapter.py - Adaptador Secundário de Política de Taxas de Juros.
"""

from __future__ import annotations
from typing import Dict
from domain.models import RiskRating
from ports.driven import InterestRatePolicyPort


class BacenMarketRatePolicyAdapter(InterestRatePolicyPort):
    def __init__(self) -> None:
        # Taxa de juros anual baseada na tabela atuarial e rating
        self._rates: Dict[RiskRating, float] = {
            RiskRating.AAA: 12.50,  # 12.5% a.a.
            RiskRating.AA: 15.00,   # 15.0% a.a.
            RiskRating.A: 18.50,    # 18.5% a.a.
            RiskRating.B: 24.00,    # 24.0% a.a.
        }

    def get_annual_rate(self, risk_rating: RiskRating) -> float:
        return self._rates.get(risk_rating, 24.00)
