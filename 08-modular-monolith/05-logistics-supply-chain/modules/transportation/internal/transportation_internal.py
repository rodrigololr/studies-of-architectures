"""Implementação Interna do Módulo Transportation (Schema: transportation)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalShipment:
    shipment_id: str
    client_name: str
    destination_city: str
    truck_plate: str
    item_code: str
    quantity: int
    cargo_value: float
    status: str = "DISPATCHED"
    dispatched_at: datetime = field(default_factory=datetime.now)


class _InternalTransportationRepository:
    def __init__(self) -> None:
        self._shipments: Dict[str, _InternalShipment] = {}

    def save(self, sh: _InternalShipment) -> None:
        self._shipments[sh.shipment_id] = sh

    def find_by_id(self, sh_id: str) -> Optional[_InternalShipment]:
        return self._shipments.get(sh_id)
