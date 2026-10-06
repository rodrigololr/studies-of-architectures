"""
use_cases/dto.py - Camada 2: DTOs para Matching de Entregadores.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MatchCourierRequestModel:
    order_id: str
    restaurant_id: str
    customer_latitude: float
    customer_longitude: float
    items_subtotal: float
    max_search_radius_km: float = 5.0


@dataclass(frozen=True)
class MatchCourierResponseModel:
    success: bool
    order_id: str
    assigned_courier_name: Optional[str]
    courier_vehicle: Optional[str]
    distance_to_restaurant_km: Optional[float]
    trip_distance_km: Optional[float]
    delivery_fee: float
    courier_payout: float
    message: str
