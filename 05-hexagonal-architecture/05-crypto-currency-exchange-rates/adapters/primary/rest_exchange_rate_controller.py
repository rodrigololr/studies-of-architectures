"""
rest_exchange_rate_controller.py - Adaptador Primário HTTP REST para Cotações Cripto.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from domain.exceptions import OracleDomainException
from ports.driver import GetAggregatedExchangeRateUseCasePort


class RestExchangeRateController:
    def __init__(self, use_case: GetAggregatedExchangeRateUseCasePort) -> None:
        self.use_case = use_case

    def handle_get_rate(self, symbol: str) -> Tuple[int, Dict[str, Any]]:
        try:
            rate = self.use_case.get_rate(symbol)
            return 200, {
                "success": True,
                "data": {
                    "symbol": rate.symbol,
                    "median_price_usd": rate.median_price,
                    "sources": rate.sources_used,
                    "samples": rate.sample_size,
                    "spread_pct": rate.spread_percentage,
                    "cached": rate.is_cached,
                    "timestamp": rate.calculated_at.isoformat(),
                },
            }
        except OracleDomainException as dom_err:
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
