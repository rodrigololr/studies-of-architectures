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
class ProductAbandonStat:
    product_id: str
    product_name: str
    abandon_occurrences: int = 0
    total_quantity_abandoned: int = 0
    total_potential_loss: float = 0.0

@dataclass
class MarketingDashboardSummary:
    total_carts_created: int = 0
    total_carts_checked_out: int = 0
    total_carts_abandoned: int = 0
    total_carts_active: int = 0
    conversion_rate_percent: float = 0.0
    total_abandoned_revenue_loss: float = 0.0
    total_recovered_revenue: float = 0.0

class AbandonedCartAnalyticsProjection:
    """
    Projeção analítica em tempo real para equipes de Marketing e Growth.
    Calcula funil de conversão, taxa de abandono e produtos com maior perda de receita.
    """

    def __init__(self):
        # Estado transitório por carrinho para mensurar o valor no momento exato do abandono
        self._temp_cart_items: Dict[str, Dict[str, dict]] = {}
        self._temp_cart_discount: Dict[str, float] = {}

        # Métricas agregadas
        self._total_created: int = 0
        self._total_checked_out: int = 0
        self._total_abandoned: int = 0
        self._total_abandoned_loss: float = 0.0
        self._total_checkout_revenue: float = 0.0

        # Estatísticas por produto
        self._product_stats: Dict[str, ProductAbandonStat] = {}

    def handle(self, event: DomainEvent) -> None:
        cart_id = event.aggregate_id

        if isinstance(event, CartCreated):
            self._total_created += 1
            self._temp_cart_items[cart_id] = {}
            self._temp_cart_discount[cart_id] = 0.0

        elif isinstance(event, ItemAdded):
            cart_items = self._temp_cart_items.setdefault(cart_id, {})
            if event.product_id in cart_items:
                cart_items[event.product_id]["quantity"] += event.quantity
            else:
                cart_items[event.product_id] = {
                    "name": event.product_name,
                    "unit_price": event.unit_price,
                    "quantity": event.quantity,
                }

        elif isinstance(event, ItemRemoved):
            if cart_id in self._temp_cart_items:
                self._temp_cart_items[cart_id].pop(event.product_id, None)

        elif isinstance(event, ItemQuantityUpdated):
            if cart_id in self._temp_cart_items and event.product_id in self._temp_cart_items[cart_id]:
                self._temp_cart_items[cart_id][event.product_id]["quantity"] = event.new_quantity

        elif isinstance(event, CouponApplied):
            self._temp_cart_discount[cart_id] = event.discount_percentage

        elif isinstance(event, CartCheckedOut):
            self._total_checked_out += 1
            self._total_checkout_revenue += event.total_amount
            # Limpa estado temporário
            self._temp_cart_items.pop(cart_id, None)
            self._temp_cart_discount.pop(cart_id, None)

        elif isinstance(event, CartAbandoned):
            self._total_abandoned += 1
            cart_items = self._temp_cart_items.pop(cart_id, {})
            discount = self._temp_cart_discount.pop(cart_id, 0.0)

            subtotal = sum(item["unit_price"] * item["quantity"] for item in cart_items.values())
            loss = subtotal * (1.0 - (discount / 100.0))
            self._total_abandoned_loss += loss

            for prod_id, item_data in cart_items.items():
                if prod_id not in self._product_stats:
                    self._product_stats[prod_id] = ProductAbandonStat(
                        product_id=prod_id,
                        product_name=item_data["name"],
                    )
                stat = self._product_stats[prod_id]
                stat.abandon_occurrences += 1
                stat.total_quantity_abandoned += item_data["quantity"]
                stat.total_potential_loss += item_data["unit_price"] * item_data["quantity"]

    def get_dashboard_summary(self) -> MarketingDashboardSummary:
        active = max(0, self._total_created - self._total_checked_out - self._total_abandoned)
        rate = (self._total_checked_out / self._total_created * 100.0) if self._total_created > 0 else 0.0

        return MarketingDashboardSummary(
            total_carts_created=self._total_created,
            total_carts_checked_out=self._total_checked_out,
            total_carts_abandoned=self._total_abandoned,
            total_carts_active=active,
            conversion_rate_percent=round(rate, 2),
            total_abandoned_revenue_loss=round(self._total_abandoned_loss, 2),
            total_recovered_revenue=round(self._total_checkout_revenue, 2),
        )

    def get_top_abandoned_products(self, limit: int = 5) -> List[ProductAbandonStat]:
        stats = list(self._product_stats.values())
        stats.sort(key=lambda s: s.total_potential_loss, reverse=True)
        return stats[:limit]
