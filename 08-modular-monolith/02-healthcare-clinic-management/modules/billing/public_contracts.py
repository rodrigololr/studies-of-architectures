"""Contrato Público do Módulo Billing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class InvoiceDto:
    invoice_id: str
    appointment_id: str
    patient_id: str
    insurance_plan: str
    total_fee: float
    insurance_covered_amount: float
    patient_copay_amount: float
    status: str  # "ISSUED", "PAID"


class IBillingModule(ABC):
    @abstractmethod
    def get_by_appointment(self, appointment_id: str) -> Optional[InvoiceDto]:
        pass

    @abstractmethod
    def list_all_invoices(self) -> List[InvoiceDto]:
        pass
