"""Contrato Público do Módulo Appointments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class ScheduleAppointmentCommand:
    patient_id: str
    doctor_crm: str
    appointment_time: datetime
    consultation_fee: float


@dataclass(frozen=True)
class AppointmentSummaryDto:
    appointment_id: str
    patient_id: str
    doctor_crm: str
    appointment_time: datetime
    status: str  # "SCHEDULED", "COMPLETED", "CANCELLED"
    consultation_fee: float


@dataclass(frozen=True)
class AppointmentCompletedDomainEvent(DomainEvent):
    """Evento emitido ao término do atendimento médico da consulta."""
    appointment_id: str = ""
    patient_id: str = ""
    doctor_crm: str = ""
    consultation_fee: float = 0.0


class IAppointmentsModule(ABC):
    @abstractmethod
    def schedule(self, cmd: ScheduleAppointmentCommand) -> AppointmentSummaryDto:
        pass

    @abstractmethod
    def complete(self, appointment_id: str) -> AppointmentSummaryDto:
        pass

    @abstractmethod
    def get_by_id(self, appointment_id: str) -> Optional[AppointmentSummaryDto]:
        pass
