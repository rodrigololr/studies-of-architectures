"""
models.py - Camada de Dados (Data Layer).
Modelos para agendamento de consultas médicas e controle de status da agenda.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class AppointmentModel:
    appointment_id: str
    patient_id: str
    doctor_id: str
    doctor_specialty: str
    slot_iso: str  # Formato: "YYYY-MM-DDTHH:MM"
    reason: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
