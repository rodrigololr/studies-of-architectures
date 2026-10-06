"""
service.py - Camada de Negócio (Business Layer).

Responsável por:
- Validar se o horário da consulta está no futuro.
- Garantir que o médico não possua outra consulta no mesmo horário.
- Garantir que o paciente não esteja em outra consulta no mesmo horário.
- Cancelar consulta liberando o horário para outros pacientes.
"""

from __future__ import annotations
from datetime import datetime
import uuid
from typing import List
from business.exceptions import (
    ScheduleConflictException,
    PastDateException,
    AppointmentNotFoundException,
    InvalidAppointmentStateException,
)
from data.models import AppointmentModel, AppointmentStatus
from data.repository import AppointmentRepository


class SchedulingService:
    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    def schedule(
        self,
        patient_id: str,
        doctor_id: str,
        doctor_specialty: str,
        slot_iso: str,
        reason: str,
    ) -> AppointmentModel:
        # 1. Regra de Negócio: Não pode agendar no passado
        try:
            slot_time = datetime.fromisoformat(slot_iso)
        except ValueError:
            raise PastDateException(f"Formato de data/hora inválido: '{slot_iso}'. Use YYYY-MM-DDTHH:MM.")

        if slot_time < datetime.now():
            raise PastDateException("Não é permitido agendar consultas em datas ou horários no passado.")

        # 2. Regra de Negócio: Conflito de agenda do médico
        if self.repository.find_active_by_doctor_and_slot(doctor_id, slot_iso):
            raise ScheduleConflictException(
                f"O médico '{doctor_id}' já possui uma consulta agendada para o horário {slot_iso}."
            )

        # 3. Regra de Negócio: Conflito de agenda do paciente
        if self.repository.find_active_by_patient_and_slot(patient_id, slot_iso):
            raise ScheduleConflictException(
                f"O paciente '{patient_id}' já possui outra consulta agendada para este mesmo horário."
            )

        appointment = AppointmentModel(
            appointment_id=str(uuid.uuid4())[:8],
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_specialty=doctor_specialty,
            slot_iso=slot_iso,
            reason=reason,
            status=AppointmentStatus.SCHEDULED,
        )
        return self.repository.save(appointment)

    def cancel(self, appointment_id: str) -> AppointmentModel:
        appointment = self.repository.find_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(f"Consulta com ID '{appointment_id}' não encontrada.")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise InvalidAppointmentStateException("A consulta já se encontra cancelada.")

        appointment.status = AppointmentStatus.CANCELLED
        return self.repository.save(appointment)

    def get_doctor_schedule(self, doctor_id: str) -> List[AppointmentModel]:
        return self.repository.list_by_doctor(doctor_id)
