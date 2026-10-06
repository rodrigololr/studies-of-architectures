"""
in_memory_price_cache_adapter.py - Adaptador Secundário de Cache com TTL em memória.
"""

from __future__ import annotations
import time
from typing import Dict, Optional, Tuple
from domain.models import AggregatedRate
from ports.driven import PriceCachePort


class InMemoryPriceCacheAdapter(PriceCachePort):
    def __init__(self) -> None:
        # armazena: symbol -> (AggregatedRate, expire_timestamp)
        self._cache: Dict[str, Tuple[AggregatedRate, float]] = {}

    def get(self, symbol: str) -> Optional[AggregatedRate]:
        entry = self._cache.get(symbol)
        if not entry:
            return None
        rate, expire_at = entry
        if time.time() > expire_at:
            # Expirou
            del self._cache[symbol]
            return None
        return rate

    def set(self, symbol: str, rate: AggregatedRate, ttl_seconds: int) -> None:
        self._cache[symbol] = (rate, time.time() + ttl_seconds)

    def clear(self) -> None:
        self._cache.clear()
