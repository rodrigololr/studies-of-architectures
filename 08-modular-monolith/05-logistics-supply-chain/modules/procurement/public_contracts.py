"""Contrato Público do Módulo Procurement (Compras e Suprimentos)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class PurchaseOrderItemDto:
    item_code: str
    description: str
    quantity: int
    unit_cost: float


@dataclass(frozen=True)
class CreatePurchaseOrderCommand:
    supplier_name: str
    items: List[PurchaseOrderItemDto]


@dataclass(frozen=True)
class PurchaseOrderDto:
    po_number: str
    supplier_name: str
    items: List[PurchaseOrderItemDto]
    total_cost: float
    status: str  # "PLACED", "RECEIVED", "CANCELLED"


@dataclass(frozen=True)
class PurchaseOrderReceivedDomainEvent(DomainEvent):
    """Evento emitido quando uma remessa de compra é entregue fisicamente pela transportadora."""
    po_number: str = ""
    supplier_name: str = ""
    items: List[PurchaseOrderItemDto] = None


class IProcurementModule(ABC):
    @abstractmethod
    def create_order(self, cmd: CreatePurchaseOrderCommand) -> PurchaseOrderDto:
        pass

    @abstractmethod
    def receive_order(self, po_number: str) -> PurchaseOrderDto:
        pass
