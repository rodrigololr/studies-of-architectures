"""
domain/model/vehicle.py - Camada 1: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class VehicleCategory(str, Enum):
    COMPACT = "COMPACT"
    SUV = "SUV"
    PREMIUM = "PREMIUM"


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class Vehicle:
    vehicle_id: str
    license_plate: str
    model_name: str
    category: VehicleCategory
    daily_rate: float
    current_odometer_km: float
    current_fuel_eighths: int = 8  # 8/8 = Tanque cheio
    status: VehicleStatus = VehicleStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def mark_rented(self) -> None:
        self.status = VehicleStatus.RENTED

    def mark_returned(self, new_odometer: float, new_fuel: int) -> None:
        self.current_odometer_km = new_odometer
        self.current_fuel_eighths = new_fuel
        self.status = VehicleStatus.AVAILABLE
