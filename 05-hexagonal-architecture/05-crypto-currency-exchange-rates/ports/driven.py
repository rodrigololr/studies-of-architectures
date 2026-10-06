"""
driven.py - Portas Secundárias / Outbound do oráculo cripto.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models import CryptoQuote, AggregatedRate


class CryptoPriceProviderPort(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome da exchange ou agregador de mercado."""
        pass

    @abstractmethod
    def fetch_price(self, symbol: str) -> Optional[CryptoQuote]:
        """Consulta cotação em tempo real da exchange."""
        pass


class PriceCachePort(ABC):
    @abstractmethod
    def get(self, symbol: str) -> Optional[AggregatedRate]:
        """Recupera cotação em cache se não expirada."""
        pass

    @abstractmethod
    def set(self, symbol: str, rate: AggregatedRate, ttl_seconds: int) -> None:
        """Armazena cotação com tempo de vida."""
        pass


class PriceOracleAuditRepositoryPort(ABC):
    @abstractmethod
    def record_rate(self, rate: AggregatedRate) -> None:
        """Persiste o registro histórico auditável do oráculo."""
        pass

    @abstractmethod
    def list_history(self) -> List[AggregatedRate]:
        """Consulta as cotações geradas."""
        pass
