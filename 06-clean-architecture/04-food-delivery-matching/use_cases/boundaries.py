"""
use_cases/boundaries.py - Camada 2: Boundaries e Gateways.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from entities.models import DeliveryOrder, Courier, Restaurant
from use_cases.dto import MatchCourierRequestModel, MatchCourierResponseModel


class MatchCourierInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: MatchCourierRequestModel) -> None:
        pass


class MatchCourierOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: MatchCourierResponseModel) -> None:
        pass


class RestaurantRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        pass


class CourierRepositoryGateway(ABC):
    @abstractmethod
    def list_available_couriers(self) -> List[Courier]:
        pass

    @abstractmethod
    def update_courier(self, courier: Courier) -> None:
        pass


class OrderRepositoryGateway(ABC):
    @abstractmethod
    def save(self, order: DeliveryOrder) -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[DeliveryOrder]:
        pass
