"""
websocket_ticker_adapter.py - Adaptador Primário de Streaming / Ticker Periódico.

Simula a camada que consome periodicamente as Driver Ports para emitir
mensagens em tempo real para dashboards e clientes DeFi conectados via WebSocket.
"""

from __future__ import annotations
from ports.driver import GetAggregatedExchangeRateUseCasePort


class WebsocketTickerSubscriptionAdapter:
    def __init__(self, use_case: GetAggregatedExchangeRateUseCasePort) -> None:
        self.use_case = use_case

    def broadcast_tick(self, symbol: str) -> str:
        rate = self.use_case.get_rate(symbol)
        cache_indicator = "[CACHED]" if rate.is_cached else "[LIVE]"
        return (
            f"[WS Broadcast] {cache_indicator} {rate.symbol}: $ {rate.median_price:,.2f} "
            f"(Fontes: {len(rate.sources_used)} | Spread: {rate.spread_percentage:.2f}%)"
        )
