"""
binance_adapter.py - Adaptador Secundário para API da Binance.
"""

from __future__ import annotations
from typing import Dict, Optional
from datetime import datetime, timezone
from domain.models import CryptoQuote
from ports.driven import CryptoPriceProviderPort


class BinanceExchangeAdapter(CryptoPriceProviderPort):
    def __init__(self, prices_feed: Dict[str, float], is_online: bool = True) -> None:
        self._prices = prices_feed
        self._is_online = is_online

    @property
    def provider_name(self) -> str:
        return "Binance Spot Exchange"

    def set_online(self, status: bool) -> None:
        self._is_online = status

    def set_price(self, symbol: str, price: float) -> None:
        self._prices[symbol] = price

    def fetch_price(self, symbol: str) -> Optional[CryptoQuote]:
        if not self._is_online or symbol not in self._prices:
            return None
        return CryptoQuote(
            provider=self.provider_name,
            symbol=symbol,
            price=self._prices[symbol],
            timestamp=datetime.now(timezone.utc),
        )
