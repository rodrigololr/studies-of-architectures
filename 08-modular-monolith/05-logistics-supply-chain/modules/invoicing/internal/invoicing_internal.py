"""Implementação Interna do Módulo Invoicing (Schema: invoicing)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class _InternalNFe:
    nfe_key: str
    shipment_id: str
    client_name: str
    cargo_value: float
    icms_tax: float
    ipi_tax: float
    total_amount: float
    status: str = "AUTHORIZED"
    issued_at: datetime = field(default_factory=datetime.now)


class _InternalInvoicingRepository:
    def __init__(self) -> None:
        self._invoices: Dict[str, _InternalNFe] = {}

    def save(self, nfe: _InternalNFe) -> None:
        self._invoices[nfe.nfe_key] = nfe

    def find_by_shipment(self, shipment_id: str) -> Optional[_InternalNFe]:
        for nfe in self._invoices.values():
            if nfe.shipment_id == shipment_id:
                return nfe
        return None

    def list_all(self) -> List[_InternalNFe]:
        return list(self._invoices.values())
