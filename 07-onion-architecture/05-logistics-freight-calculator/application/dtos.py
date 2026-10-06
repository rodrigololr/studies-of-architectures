"""Data Transfer Objects (DTOs) para cálculo de frete."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class CargoItemInputDto:
    """Dados de entrada de cada item da remessa."""
    description: str
    weight_kg: float
    length_m: float
    width_m: float
    height_m: float
    declared_value: float
    is_hazardous: bool = False
    is_fragile: bool = False


@dataclass(frozen=True)
class CalculateFreightQuoteCommand:
    """Comando de cotação de frete."""
    shipper_name: str
    origin_city: str
    destination_city: str
    distance_km: float
    truck_type: str
    items: List[CargoItemInputDto]


@dataclass(frozen=True)
class FreightQuoteResponseDto:
    """Resultado detalhado da cotação."""
    quote_id: str
    truck_type: str
    physical_weight_kg: float
    volume_m3: float
    taxable_weight_kg: float
    distance_km: float
    breakdown: Dict[str, float]
    total_freight_cost: float


@dataclass(frozen=True)
class ConfirmFreightOrderCommand:
    """Comando para confirmar despacho de frete cotado."""
    order_id: str


@dataclass(frozen=True)
class FreightOrderResponseDto:
    """Resultado da confirmação de ordem."""
    order_id: str
    status: str
    shipper_name: str
    origin_city: str
    destination_city: str
    total_cost: float
    message: str
