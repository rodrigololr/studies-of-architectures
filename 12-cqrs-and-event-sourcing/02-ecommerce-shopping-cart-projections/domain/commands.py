from dataclasses import dataclass

@dataclass(frozen=True)
class CreateCartCommand:
    cart_id: str
    customer_id: str

@dataclass(frozen=True)
class AddItemCommand:
    cart_id: str
    product_id: str
    product_name: str
    unit_price: float
    quantity: int = 1

@dataclass(frozen=True)
class RemoveItemCommand:
    cart_id: str
    product_id: str

@dataclass(frozen=True)
class UpdateQuantityCommand:
    cart_id: str
    product_id: str
    new_quantity: int

@dataclass(frozen=True)
class ApplyCouponCommand:
    cart_id: str
    coupon_code: str
    discount_percentage: float

@dataclass(frozen=True)
class CheckoutCartCommand:
    cart_id: str
    payment_method: str = "CREDIT_CARD"

@dataclass(frozen=True)
class AbandonCartCommand:
    cart_id: str
    abandon_reason: str = "SESSION_TIMEOUT"
