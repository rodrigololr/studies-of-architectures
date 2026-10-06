"""Implementações em memória dos repositórios (Ring 4 - Infrastructure)."""

from typing import Dict, Optional, List
from domain.model.freight_order import FreightOrder
from domain.model.vehicle_capacity import VehicleSpecification, TruckType
from application.interfaces import IFreightOrderRepository, IVehicleSpecificationRepository


class InMemoryFreightOrderRepository(IFreightOrderRepository):
    """Repositório em memória para persistência de ordens de frete."""
    def __init__(self) -> None:
        self._orders: Dict[str, FreightOrder] = {}

    def save(self, order: FreightOrder) -> None:
        self._orders[order.order_id] = order

    def get_by_id(self, order_id: str) -> Optional[FreightOrder]:
        return self._orders.get(order_id)

    def list_all(self) -> List[FreightOrder]:
        return list(self._orders.values())


class InMemoryVehicleSpecificationRepository(IVehicleSpecificationRepository):
    """Repositório em memória com especificações técnicas da frota disponível."""
    def __init__(self, specs: Optional[Dict[TruckType, VehicleSpecification]] = None) -> None:
        self._specs = specs or {
            TruckType.VUC: VehicleSpecification(
                truck_type=TruckType.VUC,
                max_payload_kg=3000.0,
                max_volume_m3=18.0,
                cost_per_km=4.50,
                allows_hazardous=False,
            ),
            TruckType.TOCO: VehicleSpecification(
                truck_type=TruckType.TOCO,
                max_payload_kg=6000.0,
                max_volume_m3=30.0,
                cost_per_km=6.20,
                allows_hazardous=True,
            ),
            TruckType.TRUCK: VehicleSpecification(
                truck_type=TruckType.TRUCK,
                max_payload_kg=14000.0,
                max_volume_m3=55.0,
                cost_per_km=8.80,
                allows_hazardous=True,
            ),
            TruckType.CARRETA: VehicleSpecification(
                truck_type=TruckType.CARRETA,
                max_payload_kg=25000.0,
                max_volume_m3=90.0,
                cost_per_km=12.50,
                allows_hazardous=True,
            ),
        }

    def get_by_type(self, truck_type: TruckType) -> Optional[VehicleSpecification]:
        return self._specs.get(truck_type)
