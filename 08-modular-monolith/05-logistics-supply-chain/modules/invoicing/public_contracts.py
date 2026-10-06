"""Contrato Público do Módulo Invoicing (Faturamento Fiscal e NF-e)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class FiscalInvoiceDto:
    nfe_key: str
    shipment_id: str
    client_name: str
    total_cargo_value: float
    icms_tax: float
    ipi_tax: float
    total_invoice_amount: float
    status: str  # "AUTHORIZED"


class IInvoicingModule(ABC):
    @abstractmethod
    def get_by_shipment(self, shipment_id: str) -> Optional[FiscalInvoiceDto]:
        pass

    @abstractmethod
    def list_all(self) -> List[FiscalInvoiceDto]:
        pass
