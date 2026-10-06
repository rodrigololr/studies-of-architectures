"""Modelos de veículos e especificações de capacidade física."""

from dataclasses import dataclass
from enum import Enum


class TruckType(Enum):
    VUC = "VUC"          # Veículo Urbano de Carga (Até 3.000 kg, 18 m3)
    TOCO = "TOCO"        # Caminhão Semipesado 2 eixos (Até 6.000 kg, 30 m3)
    TRUCK = "TRUCK"      # Caminhão Pesado 3 eixos (Até 14.000 kg, 55 m3)
    CARRETA = "CARRETA"  # Carreta articulada (Até 25.000 kg, 90 m3)


@dataclass(frozen=True)
class VehicleSpecification:
    """Especificação técnica e capacidade de um veículo de carga (Value Object)."""
    truck_type: TruckType
    max_payload_kg: float
    max_volume_m3: float
    cost_per_km: float
    allows_hazardous: bool = True
