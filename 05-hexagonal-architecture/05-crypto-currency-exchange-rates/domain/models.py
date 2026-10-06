"""
models.py - Modelos de domínio do oráculo de taxas de câmbio cripto.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass(frozen=True)
class CryptoQuote:
    provider: str
    symbol: str  # ex: "BTC-USD", "ETH-USD"
    price: float
    timestamp: datetime


@dataclass(frozen=True)
class AggregatedRate:
    symbol: str
    median_price: float
    sources_used: List[str]
    sample_size: int
    spread_percentage: float
    calculated_at: datetime
    is_cached: bool = False
