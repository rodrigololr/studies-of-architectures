"""Implementação Interna Privada do Módulo Appointments."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalAppointment:
    appointment_id: str
    patient_id: str
    doctor_crm: str
    appointment_time: datetime
    status: str  # "SCHEDULED", "COMPLETED", "CANCELLED"
    consultation_fee: float


class _InternalAppointmentRepository:
    def __init__(self) -> None:
        self._db: Dict[str, _InternalAppointment] = {}

    def save(self, appt: _InternalAppointment) -> None:
        self._db[appt.appointment_id] = appt

    def find_by_id(self, appt_id: str) -> Optional[_InternalAppointment]:
        return self._db.get(appt_id)
