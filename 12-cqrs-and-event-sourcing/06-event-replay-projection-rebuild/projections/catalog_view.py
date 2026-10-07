from dataclasses import dataclass
from typing import Dict, List, Optional
from domain.events import (
    DomainEvent,
    ProductCreated,
    PriceChanged,
    ProductPurchased,
)

@dataclass
class CatalogItemView:
    product_id: str
    name: str
    category: str
    current_price: float
    total_units_sold: int = 0

class CurrentCatalogProjection:
    """
    Projeção Legada (Versão 1.0): Mantém apenas o catálogo ativo e unidades vendidas.
    """

    def __init__(self):
        self._items: Dict[str, CatalogItemView] = {}

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, ProductCreated):
            self._items[event.aggregate_id] = CatalogItemView(
                product_id=event.aggregate_id,
                name=event.product_name,
                category=event.category,
                current_price=event.initial_price,
            )
        elif isinstance(event, PriceChanged):
            item = self._items.get(event.aggregate_id)
            if item:
                item.current_price = event.new_price
        elif isinstance(event, ProductPurchased):
            item = self._items.get(event.aggregate_id)
            if item:
                item.total_units_sold += event.quantity

    def get_all(self) -> List[CatalogItemView]:
        return list(self._items.values())

    def get_by_id(self, product_id: str) -> Optional[CatalogItemView]:
        return self._items.get(product_id)
