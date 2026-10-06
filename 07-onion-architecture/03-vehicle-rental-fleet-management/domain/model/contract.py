"""
domain/model/contract.py - Camada 1: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from domain.model.vehicle import Vehicle
from domain.model.inspection import InspectionReport


class ContractStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class RentalContract:
    contract_id: str
    customer_name: str
    vehicle: Vehicle
    rental_days: int
    checkout_inspection: InspectionReport
    checkin_inspection: Optional[InspectionReport] = None
    base_charge: float = 0.0
    extra_fees: float = 0.0
    total_charged: float = 0.0
    status: ContractStatus = ContractStatus.OPEN
    created_at: datetime = datetime.now(timezone.utc)

    def close_contract(self, checkin: InspectionReport, extra_fees: float) -> None:
        self.checkin_inspection = checkin
        self.extra_fees = extra_fees
        self.total_charged = round(self.base_charge + extra_fees, 2)
        self.status = ContractStatus.CLOSED
        self.vehicle.mark_returned(checkin.odometer_km, checkin.fuel_level_eighths)
