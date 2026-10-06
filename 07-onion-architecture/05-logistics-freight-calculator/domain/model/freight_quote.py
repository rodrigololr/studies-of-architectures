"""Resultado da cotação de frete (Value Object imutável)."""

from dataclasses import dataclass, field
from typing import Dict
from .vehicle_capacity import TruckType


@dataclass(frozen=True)
class FreightQuote:
    """Cotação detalhada de frete gerada pelo Domain Service (Value Object)."""
    selected_truck_type: TruckType
    total_physical_weight_kg: float
    total_volume_m3: float
    taxable_weight_kg: float  # Maior entre peso físico e peso cubado
    distance_km: float
    base_transport_cost: float
    toll_cost: float
    gris_and_insurance_cost: float  # Gerenciamento de Risco + Seguro Ad-Valorem
    hazardous_fee: float
    fragile_fee: float
    total_freight_cost: float
    breakdown: Dict[str, float] = field(default_factory=dict)
