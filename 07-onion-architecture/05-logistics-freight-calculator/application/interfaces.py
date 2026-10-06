"""Interfaces abstratas da aplicação (Portas / Contratos)."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.model.freight_order import FreightOrder
from domain.model.vehicle_capacity import VehicleSpecification, TruckType


class IFreightOrderRepository(ABC):
    """Contrato para persistência de ordens de frete."""
    @abstractmethod
    def save(self, order: FreightOrder) -> None:
        pass

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[FreightOrder]:
        pass

    @abstractmethod
    def list_all(self) -> List[FreightOrder]:
        pass


class IVehicleSpecificationRepository(ABC):
    """Contrato para consulta de especificações técnicas da frota."""
    @abstractmethod
    def get_by_type(self, truck_type: TruckType) -> Optional[VehicleSpecification]:
        pass


class ITollRateApiGateway(ABC):
    """Contrato para serviço externo de consulta de pedágios entre cidades."""
    @abstractmethod
    def calculate_tolls(self, origin: str, destination: str, truck_type: TruckType) -> float:
        pass
