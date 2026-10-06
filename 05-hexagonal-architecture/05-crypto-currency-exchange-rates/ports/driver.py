"""
driver.py - Portas Primárias / Inbound do oráculo cripto.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from domain.models import AggregatedRate


class GetAggregatedExchangeRateUseCasePort(ABC):
    @abstractmethod
    def get_rate(self, symbol: str) -> AggregatedRate:
        """Obtém a taxa ponderada/mediana agregada entre os provedores de mercado."""
        pass
