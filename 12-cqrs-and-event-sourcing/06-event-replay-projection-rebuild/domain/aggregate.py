from typing import List
from domain.events import (
    DomainEvent,
    ProductCreated,
    PriceChanged,
    ProductPurchased,
    ProductReturned,
)

class ProductAggregate:
    """
    Agregado Raiz de Produto.
    """

    def __init__(self, product_id: str):
        self.product_id: str = product_id
        self.name: str = ""
        self.category: str = ""
        self.current_price: float = 0.0
        self.is_active: bool = False
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
        for e in events:
            self._apply(e)
        self._uncommitted_events.clear()

    def _record_that(self, event: DomainEvent) -> None:
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        self.version = event.version

        if isinstance(event, ProductCreated):
            self.name = event.product_name
            self.category = event.category
            self.current_price = event.initial_price
            self.is_active = True
        elif isinstance(event, PriceChanged):
            self.current_price = event.new_price

    # =========================================================================
    # AÇÕES DE NEGÓCIO
    # =========================================================================

    def create(self, name: str, category: str, initial_price: float) -> None:
        if self.is_active:
            raise ValueError(f"Produto {self.product_id} já cadastrado.")
        if initial_price <= 0:
            raise ValueError("Preço inicial deve ser positivo.")

        self._record_that(
            ProductCreated(
                aggregate_id=self.product_id,
                version=self.version + 1,
                product_name=name,
                category=category,
                initial_price=initial_price,
            )
        )

    def change_price(self, new_price: float, reason: str = "Ajuste de margem") -> None:
        if not self.is_active:
            raise ValueError("Produto inativo.")
        if new_price <= 0:
            raise ValueError("Novo preço deve ser positivo.")
        if new_price == self.current_price:
            return

        self._record_that(
            PriceChanged(
                aggregate_id=self.product_id,
                version=self.version + 1,
                old_price=self.current_price,
                new_price=new_price,
                reason=reason,
            )
        )

    def record_purchase(self, order_id: str, quantity: int = 1) -> None:
        if not self.is_active:
            raise ValueError("Produto inativo.")
        if quantity <= 0:
            raise ValueError("Quantidade comprada deve ser maior que zero.")

        self._record_that(
            ProductPurchased(
                aggregate_id=self.product_id,
                version=self.version + 1,
                order_id=order_id,
                unit_price=self.current_price,
                quantity=quantity,
            )
        )

    def record_return(self, order_id: str, quantity: int, refund_amount: float, return_reason: str) -> None:
        if not self.is_active:
            raise ValueError("Produto inativo.")
        if quantity <= 0 or refund_amount <= 0:
            raise ValueError("Dados de devolução inválidos.")

        self._record_that(
            ProductReturned(
                aggregate_id=self.product_id,
                version=self.version + 1,
                order_id=order_id,
                quantity=quantity,
                refund_amount=refund_amount,
                return_reason=return_reason,
            )
        )
