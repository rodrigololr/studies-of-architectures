from domain.commands import PlaceLimitOrderCommand, CancelOrderCommand
from domain.aggregate import OrderBookAggregate
from infrastructure.event_store import AppendOnlyEventStore

class OrderBookCommandHandler:
    """
    Orquestrador de comandos de negociação no livro de ofertas.
    """

    def __init__(self, event_store: AppendOnlyEventStore):
        self._event_store = event_store

    def handle_place_order(self, cmd: PlaceLimitOrderCommand) -> None:
        stream = self._event_store.read_stream(cmd.pair_symbol)
        aggregate = OrderBookAggregate(cmd.pair_symbol)
        aggregate.rehydrate(stream)

        aggregate.place_limit_order(
            order_id=cmd.order_id,
            side=cmd.side,
            price=cmd.price,
            quantity=cmd.quantity,
        )

        self._event_store.append_events(cmd.pair_symbol, aggregate.uncommitted_events)
        aggregate.clear_uncommitted_events()

    def handle_cancel_order(self, cmd: CancelOrderCommand) -> None:
        stream = self._event_store.read_stream(cmd.pair_symbol)
        aggregate = OrderBookAggregate(cmd.pair_symbol)
        aggregate.rehydrate(stream)

        aggregate.cancel_order(order_id=cmd.order_id, reason=cmd.reason)

        self._event_store.append_events(cmd.pair_symbol, aggregate.uncommitted_events)
        aggregate.clear_uncommitted_events()
