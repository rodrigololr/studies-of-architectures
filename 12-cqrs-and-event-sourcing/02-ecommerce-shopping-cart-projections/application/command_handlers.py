from domain.commands import (
    CreateCartCommand,
    AddItemCommand,
    RemoveItemCommand,
    UpdateQuantityCommand,
    ApplyCouponCommand,
    CheckoutCartCommand,
    AbandonCartCommand,
)
from domain.aggregate import ShoppingCartAggregate
from infrastructure.event_store import AppendOnlyEventStore

class ShoppingCartCommandHandler:
    """
    Orquestrador dos comandos de carrinho.
    Carrega stream, re-hidrata agregado, executa validações e comita novos eventos.
    """

    def __init__(self, event_store: AppendOnlyEventStore):
        self._event_store = event_store

    def _execute(self, cart_id: str, action) -> None:
        stream = self._event_store.read_stream(cart_id)
        expected_version = len(stream)

        aggregate = ShoppingCartAggregate(cart_id)
        aggregate.rehydrate(stream)

        action(aggregate)

        self._event_store.append_events(
            stream_id=cart_id,
            events=aggregate.uncommitted_events,
            expected_version=expected_version,
        )
        aggregate.clear_uncommitted_events()

    def handle_create_cart(self, cmd: CreateCartCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.create(cmd.customer_id))

    def handle_add_item(self, cmd: AddItemCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.add_item(cmd.product_id, cmd.product_name, cmd.unit_price, cmd.quantity))

    def handle_remove_item(self, cmd: RemoveItemCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.remove_item(cmd.product_id))

    def handle_update_quantity(self, cmd: UpdateQuantityCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.update_quantity(cmd.product_id, cmd.new_quantity))

    def handle_apply_coupon(self, cmd: ApplyCouponCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.apply_coupon(cmd.coupon_code, cmd.discount_percentage))

    def handle_checkout(self, cmd: CheckoutCartCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.checkout(cmd.payment_method))

    def handle_abandon(self, cmd: AbandonCartCommand) -> None:
        self._execute(cmd.cart_id, lambda agg: agg.abandon(cmd.abandon_reason))
