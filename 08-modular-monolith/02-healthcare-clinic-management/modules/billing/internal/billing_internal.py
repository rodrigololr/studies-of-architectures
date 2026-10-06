"""Implementação Interna Privada do Módulo Billing (Schema: billing)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class _InternalInvoice:
    invoice_id: str
    appointment_id: str
    patient_id: str
    insurance_plan: str
    total_fee: float
    insurance_covered_amount: float
    patient_copay_amount: float
    status: str = "ISSUED"
    issued_at: datetime = field(default_factory=datetime.now)


class _InternalBillingRepository:
    def __init__(self) -> None:
        self._invoices: Dict[str, _InternalInvoice] = {}

    def save(self, inv: _InternalInvoice) -> None:
        self._invoices[inv.invoice_id] = inv

    def find_by_appointment(self, appt_id: str) -> Optional[_InternalInvoice]:
        for inv in self._invoices.values():
            if inv.appointment_id == appt_id:
                return inv
        return None

    def list_all(self) -> List[_InternalInvoice]:
        return list(self._invoices.values())
