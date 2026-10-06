"""Ponto de Entrada e Facade do Módulo Billing."""

import uuid
from typing import Optional, List
from shared.events import InProcessEventBus
from modules.patients.public_contracts import IPatientsModule
from modules.appointments.public_contracts import AppointmentCompletedDomainEvent
from modules.billing.public_contracts import IBillingModule, InvoiceDto
from modules.billing.internal.billing_internal import (
    _InternalInvoice,
    _InternalBillingRepository,
)


class BillingModule(IBillingModule):
    """Facade do módulo Billing.
    
    Escuta reativamente o evento AppointmentCompletedDomainEvent para gerar a fatura.
    """
    def __init__(self, patients_module: IPatientsModule, event_bus: InProcessEventBus) -> None:
        self._patients = patients_module
        self._bus = event_bus
        self._repo = _InternalBillingRepository()

        # Inscrição reativa no barramento de eventos intra-processo
        self._bus.subscribe(AppointmentCompletedDomainEvent, self._on_appointment_completed)

    def _on_appointment_completed(self, event: AppointmentCompletedDomainEvent) -> None:
        """Handler de evento executado automaticamente quando uma consulta termina."""
        patient = self._patients.get_patient(event.patient_id)
        plan = patient.insurance_plan.upper() if patient else "PARTICULAR"

        total_fee = event.consultation_fee
        if plan == "PARTICULAR":
            covered = 0.0
            copay = total_fee
        else:
            # Convênios cobrem 80% e paciente arca com 20% de coparticipação
            covered = round(total_fee * 0.80, 2)
            copay = round(total_fee * 0.20, 2)

        inv_id = f"INV_{uuid.uuid4().hex[:8].upper()}"
        invoice = _InternalInvoice(
            invoice_id=inv_id,
            appointment_id=event.appointment_id,
            patient_id=event.patient_id,
            insurance_plan=plan,
            total_fee=total_fee,
            insurance_covered_amount=covered,
            patient_copay_amount=copay,
        )
        self._repo.save(invoice)

    def get_by_appointment(self, appointment_id: str) -> Optional[InvoiceDto]:
        inv = self._repo.find_by_appointment(appointment_id)
        if not inv:
            return None
        return InvoiceDto(
            invoice_id=inv.invoice_id,
            appointment_id=inv.appointment_id,
            patient_id=inv.patient_id,
            insurance_plan=inv.insurance_plan,
            total_fee=inv.total_fee,
            insurance_covered_amount=inv.insurance_covered_amount,
            patient_copay_amount=inv.patient_copay_amount,
            status=inv.status,
        )

    def list_all_invoices(self) -> List[InvoiceDto]:
        return [
            InvoiceDto(
                invoice_id=i.invoice_id,
                appointment_id=i.appointment_id,
                patient_id=i.patient_id,
                insurance_plan=i.insurance_plan,
                total_fee=i.total_fee,
                insurance_covered_amount=i.insurance_covered_amount,
                patient_copay_amount=i.patient_copay_amount,
                status=i.status,
            )
            for i in self._repo.list_all()
        ]
