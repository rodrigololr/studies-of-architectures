"""
repository.py - Camada de Dados (Data Layer).
Acesso e persistência da agenda médica e detecção de sobreposição de slots.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from data.models import AppointmentModel, AppointmentStatus


class AppointmentRepository:
    def __init__(self) -> None:
        self._table: Dict[str, AppointmentModel] = {}

    def save(self, appointment: AppointmentModel) -> AppointmentModel:
        self._table[appointment.appointment_id] = appointment
        return appointment

    def find_by_id(self, appointment_id: str) -> Optional[AppointmentModel]:
        return self._table.get(appointment_id)

    def find_active_by_doctor_and_slot(self, doctor_id: str, slot_iso: str) -> Optional[AppointmentModel]:
        for app in self._table.values():
            if (
                app.doctor_id == doctor_id
                and app.slot_iso == slot_iso
                and app.status == AppointmentStatus.SCHEDULED
            ):
                return app
        return None

    def find_active_by_patient_and_slot(self, patient_id: str, slot_iso: str) -> Optional[AppointmentModel]:
        for app in self._table.values():
            if (
                app.patient_id == patient_id
                and app.slot_iso == slot_iso
                and app.status == AppointmentStatus.SCHEDULED
            ):
                return app
        return None

    def list_by_doctor(self, doctor_id: str) -> List[AppointmentModel]:
        return [app for app in self._table.values() if app.doctor_id == doctor_id]
