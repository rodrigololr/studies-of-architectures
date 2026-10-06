"""Implementação Interna do Módulo Procurement (Schema: procurement)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from modules.procurement.public_contracts import PurchaseOrderItemDto


@dataclass
class _InternalPO:
    po_number: str
    supplier_name: str
    items: List[PurchaseOrderItemDto]
    status: str = "PLACED"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_cost(self) -> float:
        return sum(item.quantity * item.unit_cost for item in self.items)


class _InternalProcurementRepository:
    def __init__(self) -> None:
        self._pos: Dict[str, _InternalPO] = {}

    def save(self, po: _InternalPO) -> None:
        self._pos[po.po_number] = po

    def find_by_number(self, po_number: str) -> Optional[_InternalPO]:
        return self._pos.get(po_number)
