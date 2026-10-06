"""
infrastructure/repositories.py - Camada 4: Infrastructure (Casca Externa).
"""

from __future__ import annotations
from typing import Dict, List, Optional
from domain.model.vehicle import Vehicle, VehicleStatus
from domain.model.contract import RentalContract
from application.interfaces import IVehicleRepository, IRentalContractRepository


class InMemoryVehicleRepository(IVehicleRepository):
    def __init__(self, vehicles: Optional[Dict[str, Vehicle]] = None) -> None:
        self._vehicles: Dict[str, Vehicle] = dict(vehicles or {})

    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        return self._vehicles.get(vehicle_id)

    def save(self, vehicle: Vehicle) -> None:
        self._vehicles[vehicle.vehicle_id] = vehicle

    def list_available(self) -> List[Vehicle]:
        return [v for v in self._vehicles.values() if v.status == VehicleStatus.AVAILABLE]


class InMemoryRentalContractRepository(IRentalContractRepository):
    def __init__(self) -> None:
        self._contracts: Dict[str, RentalContract] = {}

    def save(self, contract: RentalContract) -> None:
        self._contracts[contract.contract_id] = contract

    def find_by_id(self, contract_id: str) -> Optional[RentalContract]:
        return self._contracts.get(contract_id)
