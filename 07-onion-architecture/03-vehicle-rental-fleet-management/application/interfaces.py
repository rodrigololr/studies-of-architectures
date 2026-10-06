"""
application/interfaces.py - Camada 3: Application Interfaces.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.model.vehicle import Vehicle
from domain.model.contract import RentalContract


class IVehicleRepository(ABC):
    @abstractmethod
    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        pass

    @abstractmethod
    def save(self, vehicle: Vehicle) -> None:
        pass

    @abstractmethod
    def list_available(self) -> List[Vehicle]:
        pass


class IRentalContractRepository(ABC):
    @abstractmethod
    def save(self, contract: RentalContract) -> None:
        pass

    @abstractmethod
    def find_by_id(self, contract_id: str) -> Optional[RentalContract]:
        pass


class IPaymentSettlementGateway(ABC):
    @abstractmethod
    def process_charge(self, customer_name: str, amount: float, description: str) -> bool:
        pass
