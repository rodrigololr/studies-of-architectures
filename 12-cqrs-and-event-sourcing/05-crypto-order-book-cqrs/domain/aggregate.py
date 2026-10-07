from dataclasses import dataclass
from typing import Dict, List, Optional
import uuid
from domain.events import (
    DomainEvent,
    OrderPlaced,
    OrderMatched,
    OrderCancelled,
)

@dataclass
class RestingOrder:
    order_id: str
    side: str
    price: float
    remaining_quantity: float

class OrderBookAggregate:
    """
    Agregado do Livro de Ofertas e Motor de Casamento (Matching Engine).
    Executa matching atômico de ordens limite em memória e emite eventos para o Event Store.
    """

    def __init__(self, pair_symbol: str):
        self.pair_symbol: str = pair_symbol
        self.version: int = 0
        self.orders: Dict[str, RestingOrder] = {}
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

        if isinstance(event, OrderPlaced):
            self.orders[event.order_id] = RestingOrder(
                order_id=event.order_id,
                side=event.side,
                price=event.price,
                remaining_quantity=event.quantity,
            )
        elif isinstance(event, OrderMatched):
            # Atualiza o maker (ordem passiva que estava no livro)
            maker = self.orders.get(event.maker_order_id)
            if maker:
                maker.remaining_quantity -= event.executed_quantity
                if maker.remaining_quantity <= 0.0000001:
                    self.orders.pop(event.maker_order_id, None)

        elif isinstance(event, OrderCancelled):
            self.orders.pop(event.order_id, None)

    # =========================================================================
    # REGRAS DO MOTOR DE CASAMENTO (MATCHING ENGINE)
    # =========================================================================

    def place_limit_order(self, order_id: str, side: str, price: float, quantity: float) -> None:
        if quantity <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        if price <= 0:
            raise ValueError("Preço limite deve ser positivo.")
        if order_id in self.orders:
            raise ValueError(f"Ordem {order_id} já existe.")

        remaining_qty = quantity
        side_upper = side.upper()

        if side_upper == "BUY":
            # Casamento contra Asks (vendedores passivos) com preço <= preço de compra
            # Ordenados do menor preço para o maior (Best Ask First)
            candidate_asks = [
                o for o in self.orders.values()
                if o.side == "SELL" and o.price <= price and o.remaining_quantity > 0
            ]
            candidate_asks.sort(key=lambda o: o.price)

            for ask in candidate_asks:
                if remaining_qty <= 0:
                    break
                fill_qty = min(remaining_qty, ask.remaining_quantity)
                match_price = ask.price  # Preço da ordem que já estava descansando no livro (Maker)

                trade_id = f"TRD-{uuid.uuid4().hex[:8].upper()}"
                self._record_that(
                    OrderMatched(
                        aggregate_id=self.pair_symbol,
                        version=self.version + 1,
                        trade_id=trade_id,
                        maker_order_id=ask.order_id,
                        taker_order_id=order_id,
                        match_price=match_price,
                        executed_quantity=fill_qty,
                    )
                )
                remaining_qty -= fill_qty

            # Se ainda restou quantidade não executada, descansa no livro como Bid (Maker)
            if remaining_qty > 0.0000001:
                self._record_that(
                    OrderPlaced(
                        aggregate_id=self.pair_symbol,
                        version=self.version + 1,
                        order_id=order_id,
                        side="BUY",
                        price=price,
                        quantity=remaining_qty,
                    )
                )

        elif side_upper == "SELL":
            # Casamento contra Bids (compradores passivos) com preço >= preço de venda
            # Ordenados do maior preço para o menor (Best Bid First)
            candidate_bids = [
                o for o in self.orders.values()
                if o.side == "BUY" and o.price >= price and o.remaining_quantity > 0
            ]
            candidate_bids.sort(key=lambda o: o.price, reverse=True)

            for bid in candidate_bids:
                if remaining_qty <= 0:
                    break
                fill_qty = min(remaining_qty, bid.remaining_quantity)
                match_price = bid.price

                trade_id = f"TRD-{uuid.uuid4().hex[:8].upper()}"
                self._record_that(
                    OrderMatched(
                        aggregate_id=self.pair_symbol,
                        version=self.version + 1,
                        trade_id=trade_id,
                        maker_order_id=bid.order_id,
                        taker_order_id=order_id,
                        match_price=match_price,
                        executed_quantity=fill_qty,
                    )
                )
                remaining_qty -= fill_qty

            if remaining_qty > 0.0000001:
                self._record_that(
                    OrderPlaced(
                        aggregate_id=self.pair_symbol,
                        version=self.version + 1,
                        order_id=order_id,
                        side="SELL",
                        price=price,
                        quantity=remaining_qty,
                    )
                )

    def cancel_order(self, order_id: str, reason: str = "CLIENT_REQUEST") -> None:
        order = self.orders.get(order_id)
        if not order:
            raise ValueError(f"Ordem {order_id} não encontrada ou já totalmente executada.")

        self._record_that(
            OrderCancelled(
                aggregate_id=self.pair_symbol,
                version=self.version + 1,
                order_id=order_id,
                side=order.side,
                price=order.price,
                unfilled_quantity=order.remaining_quantity,
                reason=reason,
            )
        )
