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
from domain.exceptions import (
    CartInactiveException,
    EmptyCartException,
    ProductNotFoundInCartException,
    InvalidCartOperationException,
)

class ShoppingCartAggregate:
    """
    Agregado Raiz do Carrinho de Compras E-Commerce.
    Estado reconstruído 100% via eventos históricos.
    """

    def __init__(self, cart_id: str):
        self.cart_id: str = cart_id
        self.customer_id: str = ""
        # product_id -> {"name": str, "unit_price": float, "quantity": int}
        self.items: Dict[str, Dict] = {}
        self.coupon_code: Optional[str] = None
        self.discount_percentage: float = 0.0
        self.is_created: bool = False
        self.is_checked_out: bool = False
        self.is_abandoned: bool = False
        self.version: int = 0
        self._uncommitted_events: List[DomainEvent] = []

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # =========================================================================
    # RE-HIDRATAÇÃO
    # =========================================================================

    def rehydrate(self, events: List[DomainEvent]) -> None:
        for event in events:
            self._apply(event)
            self.version = event.version
        self._uncommitted_events.clear()

    def _record_that(self, event: DomainEvent) -> None:
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        if isinstance(event, CartCreated):
            self.customer_id = event.customer_id
            self.is_created = True
        elif isinstance(event, ItemAdded):
            if event.product_id in self.items:
                self.items[event.product_id]["quantity"] += event.quantity
            else:
                self.items[event.product_id] = {
                    "name": event.product_name,
                    "unit_price": event.unit_price,
                    "quantity": event.quantity,
                }
        elif isinstance(event, ItemRemoved):
            self.items.pop(event.product_id, None)
        elif isinstance(event, ItemQuantityUpdated):
            if event.product_id in self.items:
                self.items[event.product_id]["quantity"] = event.new_quantity
        elif isinstance(event, CouponApplied):
            self.coupon_code = event.coupon_code
            self.discount_percentage = event.discount_percentage
        elif isinstance(event, CartCheckedOut):
            self.is_checked_out = True
        elif isinstance(event, CartAbandoned):
            self.is_abandoned = True

    # =========================================================================
    # REGRAS E MÉTODOS DE NEGÓCIO
    # =========================================================================

    def create(self, customer_id: str) -> None:
        if self.is_created:
            raise InvalidCartOperationException(f"Carrinho '{self.cart_id}' já foi criado.")
        if not customer_id:
            raise InvalidCartOperationException("Identificador do cliente é obrigatório.")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            CartCreated(
                aggregate_id=self.cart_id,
                version=next_version,
                customer_id=customer_id,
            )
        )

    def add_item(self, product_id: str, product_name: str, unit_price: float, quantity: int = 1) -> None:
        self._assert_can_modify()
        if quantity <= 0:
            raise InvalidCartOperationException(f"Quantidade deve ser maior que zero. Recebido: {quantity}")
        if unit_price < 0:
            raise InvalidCartOperationException(f"Preço unitário não pode ser negativo. Recebido: {unit_price}")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            ItemAdded(
                aggregate_id=self.cart_id,
                version=next_version,
                product_id=product_id,
                product_name=product_name,
                unit_price=unit_price,
                quantity=quantity,
            )
        )

    def remove_item(self, product_id: str) -> None:
        self._assert_can_modify()
        if product_id not in self.items:
            raise ProductNotFoundInCartException(f"Produto '{product_id}' não existe no carrinho.")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            ItemRemoved(
                aggregate_id=self.cart_id,
                version=next_version,
                product_id=product_id,
            )
        )

    def update_quantity(self, product_id: str, new_quantity: int) -> None:
        self._assert_can_modify()
        if product_id not in self.items:
            raise ProductNotFoundInCartException(f"Produto '{product_id}' não existe no carrinho.")
        if new_quantity <= 0:
            raise InvalidCartOperationException("Quantidade atualizada deve ser maior que zero.")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            ItemQuantityUpdated(
                aggregate_id=self.cart_id,
                version=next_version,
                product_id=product_id,
                new_quantity=new_quantity,
            )
        )

    def apply_coupon(self, coupon_code: str, discount_percentage: float) -> None:
        self._assert_can_modify()
        if not (0 < discount_percentage <= 100):
            raise InvalidCartOperationException("Desconto do cupom deve estar entre 1% e 100%.")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            CouponApplied(
                aggregate_id=self.cart_id,
                version=next_version,
                coupon_code=coupon_code.strip().upper(),
                discount_percentage=discount_percentage,
            )
        )

    def checkout(self, payment_method: str = "CREDIT_CARD") -> float:
        self._assert_can_modify()
        if not self.items:
            raise EmptyCartException("Não é permitido finalizar um carrinho sem itens.")

        subtotal = sum(item["unit_price"] * item["quantity"] for item in self.items.values())
        discount_value = subtotal * (self.discount_percentage / 100.0)
        total_amount = max(0.0, subtotal - discount_value)

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            CartCheckedOut(
                aggregate_id=self.cart_id,
                version=next_version,
                total_amount=round(total_amount, 2),
                payment_method=payment_method,
            )
        )
        return round(total_amount, 2)

    def abandon(self, reason: str = "SESSION_TIMEOUT") -> None:
        self._assert_can_modify()
        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            CartAbandoned(
                aggregate_id=self.cart_id,
                version=next_version,
                abandon_reason=reason,
            )
        )

    def _assert_can_modify(self) -> None:
        if not self.is_created:
            raise CartInactiveException(f"Carrinho '{self.cart_id}' não foi inicializado.")
        if self.is_checked_out:
            raise CartInactiveException(f"Carrinho '{self.cart_id}' já foi finalizado.")
        if self.is_abandoned:
            raise CartInactiveException(f"Carrinho '{self.cart_id}' foi abandonado.")
