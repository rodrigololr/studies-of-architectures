"""Entidade de Pedido / Ordem de Frete (Freight Order)."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from .cargo_item import CargoItem
from .freight_quote import FreightQuote
from .exceptions import InvalidFreightOrderStateException


class FreightOrderStatus(Enum):
    QUOTED = "QUOTED"
    CONFIRMED = "CONFIRMED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass
class FreightOrder:
    """Entidade do Domínio: Ordem de Transporte de Frete."""
    order_id: str
    shipper_name: str  # Embarcador / Cliente
    origin_city: str
    destination_city: str
    distance_km: float
    items: List[CargoItem]
    quote: FreightQuote
    status: FreightOrderStatus = FreightOrderStatus.QUOTED
    created_at: datetime = field(default_factory=datetime.now)

    def confirm_dispatch(self) -> None:
        """Confirma a contratação e despacho do frete."""
        if self.status != FreightOrderStatus.QUOTED:
            raise InvalidFreightOrderStateException(
                f"Não é possível despachar pedido com status '{self.status.value}'."
            )
        self.status = FreightOrderStatus.CONFIRMED

    def mark_in_transit(self) -> None:
        if self.status != FreightOrderStatus.CONFIRMED:
            raise InvalidFreightOrderStateException("Carga só pode iniciar trânsito após confirmação.")
        self.status = FreightOrderStatus.IN_TRANSIT

    def mark_delivered(self) -> None:
        if self.status != FreightOrderStatus.IN_TRANSIT:
            raise InvalidFreightOrderStateException("Carga só pode ser entregue se estiver em trânsito.")
        self.status = FreightOrderStatus.DELIVERED
