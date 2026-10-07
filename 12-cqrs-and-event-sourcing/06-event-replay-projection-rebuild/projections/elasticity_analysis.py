from dataclasses import dataclass, field
from typing import Dict, List, Optional
from domain.events import (
    DomainEvent,
    ProductCreated,
    PriceChanged,
    ProductPurchased,
    ProductReturned,
)

@dataclass
class PriceTierStat:
    price: float
    units_sold: int = 0
    gross_revenue: float = 0.0
    units_returned: int = 0
    total_refunded: float = 0.0

    @property
    def return_rate_percent(self) -> float:
        if self.units_sold == 0:
            return 0.0
        return round((self.units_returned / self.units_sold) * 100.0, 1)

    @property
    def net_revenue(self) -> float:
        return round(self.gross_revenue - self.total_refunded, 2)

@dataclass
class ProductElasticitySummary:
    product_id: str
    product_name: str
    price_changes_count: int = 0
    tiers: Dict[float, PriceTierStat] = field(default_factory=dict)
    total_gross_revenue: float = 0.0
    total_refunded_value: float = 0.0
    total_units_sold: int = 0
    total_units_returned: int = 0

    @property
    def net_revenue(self) -> float:
        return round(self.total_gross_revenue - self.total_refunded_value, 2)

    @property
    def overall_return_rate_percent(self) -> float:
        if self.total_units_sold == 0:
            return 0.0
        return round((self.total_units_returned / self.total_units_sold) * 100.0, 1)

class PriceElasticityAndRefundProjection:
    """
    Nova Projeção Reconstruída (Versão 2.0).
    Calcula elasticidade de preço, volumes por faixa de valor e taxa de devolução/churn.
    """

    def __init__(self):
        # product_id -> ProductElasticitySummary
        self._summaries: Dict[str, ProductElasticitySummary] = {}
        # Rastreia o preço vigente no momento de cada compra para atribuir devoluções
        self._current_prices: Dict[str, float] = {}
        # order_id -> (product_id, unit_price)
        self._order_price_map: Dict[str, tuple[str, float]] = {}

    def handle(self, event: DomainEvent) -> None:
        p_id = event.aggregate_id

        if isinstance(event, ProductCreated):
            summary = ProductElasticitySummary(
                product_id=p_id,
                product_name=event.product_name,
            )
            # Inicializa a primeira faixa de preço
            summary.tiers[event.initial_price] = PriceTierStat(price=event.initial_price)
            self._summaries[p_id] = summary
            self._current_prices[p_id] = event.initial_price

        elif isinstance(event, PriceChanged):
            summary = self._summaries.get(p_id)
            if summary:
                summary.price_changes_count += 1
                if event.new_price not in summary.tiers:
                    summary.tiers[event.new_price] = PriceTierStat(price=event.new_price)
            self._current_prices[p_id] = event.new_price

        elif isinstance(event, ProductPurchased):
            summary = self._summaries.get(p_id)
            price = event.unit_price
            rev = price * event.quantity

            self._order_price_map[event.order_id] = (p_id, price)

            if summary:
                summary.total_units_sold += event.quantity
                summary.total_gross_revenue += rev

                tier = summary.tiers.setdefault(price, PriceTierStat(price=price))
                tier.units_sold += event.quantity
                tier.gross_revenue += rev

        elif isinstance(event, ProductReturned):
            summary = self._summaries.get(p_id)
            order_info = self._order_price_map.get(event.order_id)
            price = order_info[1] if order_info else self._current_prices.get(p_id, 0.0)

            if summary:
                summary.total_units_returned += event.quantity
                summary.total_refunded_value += event.refund_amount

                if price in summary.tiers:
                    tier = summary.tiers[price]
                    tier.units_returned += event.quantity
                    tier.total_refunded += event.refund_amount

    def get_summary(self, product_id: str) -> Optional[ProductElasticitySummary]:
        return self._summaries.get(product_id)

    def get_all_summaries(self) -> List[ProductElasticitySummary]:
        return list(self._summaries.values())
