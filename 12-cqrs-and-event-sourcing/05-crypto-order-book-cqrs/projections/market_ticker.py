from dataclasses import dataclass
from typing import Dict, Optional
from domain.events import DomainEvent, OrderMatched

@dataclass
class MarketTickerView:
    pair_symbol: str
    last_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    volume_base: float = 0.0      # Total em BTC
    volume_quote: float = 0.0     # Total em USDT
    trades_count: int = 0

class MarketTickerProjection:
    """
    Projeção do Ticker 24h de Mercado.
    Consome exclusivamente eventos de negociação concluída (OrderMatched).
    """

    def __init__(self):
        self._tickers: Dict[str, MarketTickerView] = {}

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, OrderMatched):
            pair = event.aggregate_id
            if pair not in self._tickers:
                self._tickers[pair] = MarketTickerView(
                    pair_symbol=pair,
                    last_price=event.match_price,
                    high_price=event.match_price,
                    low_price=event.match_price,
                    volume_base=event.executed_quantity,
                    volume_quote=round(event.executed_quantity * event.match_price, 2),
                    trades_count=1,
                )
            else:
                ticker = self._tickers[pair]
                ticker.last_price = event.match_price
                ticker.high_price = max(ticker.high_price, event.match_price)
                ticker.low_price = min(ticker.low_price, event.match_price)
                ticker.volume_base = round(ticker.volume_base + event.executed_quantity, 6)
                ticker.volume_quote = round(ticker.volume_quote + (event.executed_quantity * event.match_price), 2)
                ticker.trades_count += 1

    def get_ticker(self, pair_symbol: str) -> Optional[MarketTickerView]:
        return self._tickers.get(pair_symbol)
