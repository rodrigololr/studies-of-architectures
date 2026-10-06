"""
service.py - Núcleo da Aplicação (Core / Hexágono) para Oráculo de Câmbio Cripto.
"""

from __future__ import annotations
from typing import List
from datetime import datetime, timezone
from domain.models import AggregatedRate, CryptoQuote
from domain.exceptions import UnsupportedSymbolException, OracleQuorumFailedException
from ports.driver import GetAggregatedExchangeRateUseCasePort
from ports.driven import (
    CryptoPriceProviderPort,
    PriceCachePort,
    PriceOracleAuditRepositoryPort,
)


class CryptoOracleAggregatorService(GetAggregatedExchangeRateUseCasePort):
    SUPPORTED_SYMBOLS = {"BTC-USD", "ETH-USD", "SOL-USD"}

    def __init__(
        self,
        providers: List[CryptoPriceProviderPort],
        cache: PriceCachePort,
        audit_repo: PriceOracleAuditRepositoryPort,
        cache_ttl_seconds: int = 60,
        min_quorum: int = 2,
    ) -> None:
        self.providers = providers
        self.cache = cache
        self.audit_repo = audit_repo
        self.cache_ttl_seconds = cache_ttl_seconds
        self.min_quorum = min_quorum

    def get_rate(self, symbol: str) -> AggregatedRate:
        normalized_symbol = symbol.upper().strip()
        if normalized_symbol not in self.SUPPORTED_SYMBOLS:
            raise UnsupportedSymbolException(
                f"Par de moedas '{symbol}' não suportado. Permitidos: {sorted(list(self.SUPPORTED_SYMBOLS))}"
            )

        # 1. Consulta ao Cache (Driven Port)
        cached_rate = self.cache.get(normalized_symbol)
        if cached_rate:
            # Retorna valor em cache com flag explicativa
            return AggregatedRate(
                symbol=cached_rate.symbol,
                median_price=cached_rate.median_price,
                sources_used=cached_rate.sources_used,
                sample_size=cached_rate.sample_size,
                spread_percentage=cached_rate.spread_percentage,
                calculated_at=cached_rate.calculated_at,
                is_cached=True,
            )

        # 2. Coleta de Cotações nos Provedores Conectados (Driven Ports)
        valid_quotes: List[CryptoQuote] = []
        for provider in self.providers:
            try:
                quote = provider.fetch_price(normalized_symbol)
                if quote and quote.price > 0:
                    valid_quotes.append(quote)
            except Exception:
                # Falha em um provedor isolado não derruba a agregação
                continue

        # 3. Verificação de Quórum Mínimo
        if len(valid_quotes) < self.min_quorum:
            raise OracleQuorumFailedException(
                f"Quórum insuficiente para {normalized_symbol}: apenas {len(valid_quotes)} "
                f"fontes responderam (mínimo exigido: {self.min_quorum})."
            )

        # 4. Cálculo da Taxa Mediana (Robusta contra Outliers)
        sorted_prices = sorted(q.price for q in valid_quotes)
        n = len(sorted_prices)
        if n % 2 == 1:
            median_price = sorted_prices[n // 2]
        else:
            median_price = (sorted_prices[(n // 2) - 1] + sorted_prices[n // 2]) / 2.0

        median_price = round(median_price, 2)
        min_p = sorted_prices[0]
        max_p = sorted_prices[-1]
        spread_percentage = round(((max_p - min_p) / min_p) * 100.0, 4)

        # 5. Construção e Armazenamento do Resultado Agregado
        sources = [q.provider for q in valid_quotes]
        rate = AggregatedRate(
            symbol=normalized_symbol,
            median_price=median_price,
            sources_used=sources,
            sample_size=n,
            spread_percentage=spread_percentage,
            calculated_at=datetime.now(timezone.utc),
            is_cached=False,
        )

        self.cache.set(normalized_symbol, rate, self.cache_ttl_seconds)
        self.audit_repo.record_rate(rate)

        return rate
