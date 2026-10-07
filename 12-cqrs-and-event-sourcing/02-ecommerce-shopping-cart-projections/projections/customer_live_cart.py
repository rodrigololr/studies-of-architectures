from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from domain.events import (
    DomainEvent,
    CartCreated,
    ItemAdded,
    ItemRemoved,
    ItemQuantityUpdated,
    CouponApplied,
    CartCheckedOut,
    CartAbandoned,
)

@dataclass
class CartItemView:
    product_id: str
    product_name: str
    unit_price: float
    quantity: int

    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity

@dataclass
class CustomerLiveCartView:
    cart_id: str
    customer_id: str
    items: Dict[str, CartItemView] = field(default_factory=dict)
    coupon_code: Optional[str] = None
    discount_percentage: float = 0.0
    status: str = "ACTIVE"
    total_amount: float = 0.0
    version: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return sum(item.total_price for item in self.items.values())

    @property
    def discount_amount(self) -> float:
        return self.subtotal * (self.discount_percentage / 100.0)

    @property
    def computed_total(self) -> float:
        if self.status == "CHECKED_OUT":
            return self.total_amount
        return max(0.0, self.subtotal - self.discount_amount)

class CustomerLiveCartProjection:
    """
    Projeção desnormalizada em tempo real para a interface de checkout do comprador.
    """

    def __init__(self):
        self._carts: Dict[str, CustomerLiveCartView] = {}

    def handle(self, event: DomainEvent) -> None:
        cart_id = event.aggregate_id

        if isinstance(event, CartCreated):
            self._carts[cart_id] = CustomerLiveCartView(
                cart_id=cart_id,
                customer_id=event.customer_id,
                version=event.version,
                last_updated=event.timestamp,
            )
        elif isinstance(event, ItemAdded):
            cart = self._carts.get(cart_id)
            if cart:
                if event.product_id in cart.items:
                    cart.items[event.product_id].quantity += event.quantity
                else:
                    cart.items[event.product_id] = CartItemView(
                        product_id=event.product_id,
                        product_name=event.product_name,
                        unit_price=event.unit_price,
                        quantity=event.quantity,
                    )
                cart.version = event.version
                cart.last_updated = event.timestamp
        elif isinstance(event, ItemRemoved):
            cart = self._carts.get(cart_id)
            if cart:
                cart.items.pop(event.product_id, None)
                cart.version = event.version
                cart.last_updated = event.timestamp
        elif isinstance(event, ItemQuantityUpdated):
            cart = self._carts.get(cart_id)
            if cart and event.product_id in cart.items:
                cart.items[event.product_id].quantity = event.new_quantity
                cart.version = event.version
                cart.last_updated = event.timestamp
        elif isinstance(event, CouponApplied):
            cart = self._carts.get(cart_id)
            if cart:
                cart.coupon_code = event.coupon_code
                cart.discount_percentage = event.discount_percentage
                cart.version = event.version
                cart.last_updated = event.timestamp
        elif isinstance(event, CartCheckedOut):
            cart = self._carts.get(cart_id)
            if cart:
                cart.status = "CHECKED_OUT"
                cart.total_amount = event.total_amount
                cart.version = event.version
                cart.last_updated = event.timestamp
        elif isinstance(event, CartAbandoned):
            cart = self._carts.get(cart_id)
            if cart:
                cart.status = "ABANDONED"
                cart.version = event.version
                cart.last_updated = event.timestamp

    def get_cart(self, cart_id: str) -> Optional[CustomerLiveCartView]:
        return self._carts.get(cart_id)

    def get_active_carts(self) -> List[CustomerLiveCartView]:
        return [c for c in self._carts.values() if c.status == "ACTIVE"]
