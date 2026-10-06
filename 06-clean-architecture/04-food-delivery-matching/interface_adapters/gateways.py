"""
interface_adapters/gateways.py - Camada 3: Gateways e Repositórios de Delivery.
"""

from __future__ import annotations
from typing import Dict, Optional, List
from entities.models import DeliveryOrder, Courier, Restaurant
from use_cases.boundaries import (
    CourierRepositoryGateway,
    RestaurantRepositoryGateway,
    OrderRepositoryGateway,
)


class InMemoryRestaurantRepository(RestaurantRepositoryGateway):
    def __init__(self, restaurants: Optional[Dict[str, Restaurant]] = None) -> None:
        self._restaurants: Dict[str, Restaurant] = dict(restaurants or {})

    def find_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        return self._restaurants.get(restaurant_id)


class InMemoryCourierRepository(CourierRepositoryGateway):
    def __init__(self, couriers: Optional[Dict[str, Courier]] = None) -> None:
        self._couriers: Dict[str, Courier] = dict(couriers or {})

    def list_available_couriers(self) -> List[Courier]:
        return [c for c in self._couriers.values() if c.is_online and not c.is_busy]

    def update_courier(self, courier: Courier) -> None:
        self._couriers[courier.courier_id] = courier


class InMemoryOrderRepository(OrderRepositoryGateway):
    def __init__(self) -> None:
        self._orders: Dict[str, DeliveryOrder] = {}

    def save(self, order: DeliveryOrder) -> None:
        self._orders[order.order_id] = order

    def find_by_id(self, order_id: str) -> Optional[DeliveryOrder]:
        return self._orders.get(order_id)
