"""Real-Time Analytics Consumer: Agregador de métricas e GMV em tempo real."""

from events.order_events import OrderPlacedEvent


class RealTimeAnalyticsConsumer:
    def __init__(self) -> None:
        self.total_orders_count: int = 0
        self.accumulated_gmv_brl: float = 0.0

    def handle(self, event: OrderPlacedEvent) -> None:
        self.total_orders_count += 1
        self.accumulated_gmv_brl += event.total_amount

    @property
    def average_ticket_brl(self) -> float:
        if self.total_orders_count == 0:
            return 0.0
        return round(self.accumulated_gmv_brl / self.total_orders_count, 2)
