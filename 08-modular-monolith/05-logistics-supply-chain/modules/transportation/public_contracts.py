"""Contrato Público do Módulo Transportation (Gestão de Frota e Despacho de Cargas)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from shared.events import DomainEvent


@dataclass(frozen=True)
class DispatchShipmentCommand:
    client_name: str
    destination_city: str
    truck_plate: str
    item_code: str
    quantity: int
    cargo_value: float


@dataclass(frozen=True)
class ShipmentDto:
    shipment_id: str
    client_name: str
    destination_city: str
    truck_plate: str
    status: str  # "DISPATCHED", "IN_TRANSIT", "DELIVERED"
    cargo_value: float


@dataclass(frozen=True)
class ShipmentDispatchedDomainEvent(DomainEvent):
    """Evento emitido quando o caminhão é carregado e liberado para a estrada."""
    shipment_id: str = ""
    client_name: str = ""
    destination_city: str = ""
    item_code: str = ""
    quantity: int = 0
    cargo_value: float = 0.0


class ITransportationModule(ABC):
    @abstractmethod
    def dispatch(self, cmd: DispatchShipmentCommand) -> ShipmentDto:
        pass
