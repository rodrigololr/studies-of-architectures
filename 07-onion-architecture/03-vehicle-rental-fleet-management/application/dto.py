"""
application/dto.py - Camada 3: Application DTOs.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass(frozen=True)
class OpenRentalCommand:
    customer_name: str
    vehicle_id: str
    rental_days: int


@dataclass(frozen=True)
class OpenRentalResponseDto:
    success: bool
    contract_id: Optional[str]
    customer_name: str
    vehicle_model: Optional[str]
    days: int
    base_charge: float
    message: str


@dataclass(frozen=True)
class CloseRentalCommand:
    contract_id: str
    return_odometer_km: float
    return_fuel_eighths: int
    damages: List[str]


@dataclass(frozen=True)
class CloseRentalResponseDto:
    success: bool
    contract_id: str
    base_charge: float
    extra_fees: float
    fee_breakdown: Dict[str, float]
    total_charged: float
    message: str
