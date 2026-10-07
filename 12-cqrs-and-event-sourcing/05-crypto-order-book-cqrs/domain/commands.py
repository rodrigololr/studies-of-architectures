from dataclasses import dataclass

@dataclass(frozen=True)
class PlaceLimitOrderCommand:
    pair_symbol: str
    order_id: str
    side: str  # BUY ou SELL
    price: float
    quantity: float

@dataclass(frozen=True)
class CancelOrderCommand:
    pair_symbol: str
    order_id: str
    reason: str = "CLIENT_REQUEST"
