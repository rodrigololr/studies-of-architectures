"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Tuple


class VehicleType(str, Enum):
    BICYCLE = "BICYCLE"
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"


class OrderStatus(str, Enum):
    PENDING_MATCH = "PENDING_MATCH"
    ASSIGNED = "ASSIGNED"
    DELIVERED = "DELIVERED"
    UNMATCHED = "UNMATCHED"


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float

    def distance_km_to(self, other: GeoLocation) -> float:
        """
        Fórmula de Haversine pura para distância geodésica em km.
        """
        r = 6371.0  # Raio médio da Terra em km
        phi1 = math.radians(self.latitude)
        phi2 = math.radians(other.latitude)
        delta_phi = math.radians(other.latitude - self.latitude)
        delta_lambda = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 2)


@dataclass
class Courier:
    courier_id: str
    name: str
    location: GeoLocation
    vehicle: VehicleType
    is_online: bool
    is_busy: bool = False
    rating: float = 5.0

    def is_eligible_for_dispatch(self, distance_to_restaurant_km: float, max_radius_km: float) -> bool:
        """Regra de elegibilidade corporativa do entregador."""
        if not self.is_online or self.is_busy:
            return False
        # Bicicletas não realizam corridas com raio superior a 4 km
        if self.vehicle == VehicleType.BICYCLE and distance_to_restaurant_km > 4.0:
            return False
        return distance_to_restaurant_km <= max_radius_km


@dataclass(frozen=True)
class Restaurant:
    restaurant_id: str
    name: str
    location: GeoLocation


@dataclass
class DeliveryOrder:
    order_id: str
    restaurant: Restaurant
    customer_location: GeoLocation
    items_subtotal: float
    status: OrderStatus
    created_at: datetime
    assigned_courier_id: Optional[str] = None
    delivery_fee: float = 0.0
    courier_payout: float = 0.0

    def calculate_fees(self, total_distance_km: float) -> Tuple[float, float]:
        """
        Regra Corporativa de Negócio:
        Calcula a taxa de entrega cobrada do cliente e o repasse ao entregador.
        Taxa Cliente = Base R$ 5.00 + R$ 2.00 por km.
        Repasse Entregador = 80% da taxa de entrega + bônus de R$ 1.50 para motos.
        """
        fee = round(5.00 + (total_distance_km * 2.00), 2)
        payout = round(fee * 0.80, 2)
        self.delivery_fee = fee
        self.courier_payout = payout
        return fee, payout
