from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from domain.events import (
    DomainEvent,
    OrderPlaced,
    OrderMatched,
    OrderCancelled,
)

@dataclass
class PriceLevelView:
    price: float
    volume: float
    cumulative_volume: float

class L2DepthChartProjection:
    """
    Projeção desnormalizada do Gráfico de Profundidade L2 (Level 2 Order Book).
    Agrupa ordens de compra (Bids) e venda (Asks) por nível de preço em tempo real.
    """

    def __init__(self):
        # Mapeamento auxiliar: order_id -> (side, price, remaining_qty)
        self._order_index: Dict[str, dict] = {}

        # Mapeamentos de liquidez: price -> volume agregado
        self._bids_by_price: Dict[float, float] = {}
        self._asks_by_price: Dict[float, float] = {}

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, OrderPlaced):
            self._order_index[event.order_id] = {
                "side": event.side,
                "price": event.price,
                "quantity": event.quantity,
            }
            if event.side == "BUY":
                self._bids_by_price[event.price] = round(self._bids_by_price.get(event.price, 0.0) + event.quantity, 6)
            else:
                self._asks_by_price[event.price] = round(self._asks_by_price.get(event.price, 0.0) + event.quantity, 6)

        elif isinstance(event, OrderMatched):
            # A ordem maker foi total ou parcialmente preenchida
            maker = self._order_index.get(event.maker_order_id)
            if maker:
                side = maker["side"]
                price = maker["price"]
                maker["quantity"] = max(0.0, maker["quantity"] - event.executed_quantity)

                if side == "BUY":
                    new_vol = round(self._bids_by_price.get(price, 0.0) - event.executed_quantity, 6)
                    if new_vol <= 0.000001:
                        self._bids_by_price.pop(price, None)
                    else:
                        self._bids_by_price[price] = new_vol
                else:
                    new_vol = round(self._asks_by_price.get(price, 0.0) - event.executed_quantity, 6)
                    if new_vol <= 0.000001:
                        self._asks_by_price.pop(price, None)
                    else:
                        self._asks_by_price[price] = new_vol

                if maker["quantity"] <= 0.000001:
                    self._order_index.pop(event.maker_order_id, None)

        elif isinstance(event, OrderCancelled):
            maker = self._order_index.pop(event.order_id, None)
            if maker:
                side = maker["side"]
                price = maker["price"]
                qty = event.unfilled_quantity
                if side == "BUY":
                    new_vol = round(self._bids_by_price.get(price, 0.0) - qty, 6)
                    if new_vol <= 0.000001:
                        self._bids_by_price.pop(price, None)
                    else:
                        self._bids_by_price[price] = new_vol
                else:
                    new_vol = round(self._asks_by_price.get(price, 0.0) - qty, 6)
                    if new_vol <= 0.000001:
                        self._asks_by_price.pop(price, None)
                    else:
                        self._asks_by_price[price] = new_vol

    def get_bids(self, limit: int = 5) -> List[PriceLevelView]:
        sorted_prices = sorted(self._bids_by_price.keys(), reverse=True)
        levels: List[PriceLevelView] = []
        cumulative = 0.0
        for p in sorted_prices[:limit]:
            vol = self._bids_by_price[p]
            cumulative += vol
            levels.append(PriceLevelView(price=p, volume=vol, cumulative_volume=round(cumulative, 6)))
        return levels

    def get_asks(self, limit: int = 5) -> List[PriceLevelView]:
        sorted_prices = sorted(self._asks_by_price.keys())
        levels: List[PriceLevelView] = []
        cumulative = 0.0
        for p in sorted_prices[:limit]:
            vol = self._asks_by_price[p]
            cumulative += vol
            levels.append(PriceLevelView(price=p, volume=vol, cumulative_volume=round(cumulative, 6)))
        return levels

    def get_spread(self) -> Optional[float]:
        best_bid = max(self._bids_by_price.keys()) if self._bids_by_price else None
        best_ask = min(self._asks_by_price.keys()) if self._asks_by_price else None
        if best_bid is not None and best_ask is not None:
            return round(best_ask - best_bid, 2)
        return None

    def get_mid_price(self) -> Optional[float]:
        best_bid = max(self._bids_by_price.keys()) if self._bids_by_price else None
        best_ask = min(self._asks_by_price.keys()) if self._asks_by_price else None
        if best_bid is not None and best_ask is not None:
            return round((best_ask + best_bid) / 2.0, 2)
        return None
