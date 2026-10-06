"""Contrato Público do Módulo Patients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PatientDto:
    patient_id: str
    name: str
    cpf: str
    insurance_plan: str  # ex: "UNIMED", "BRADESCO", "PARTICULAR"
    is_active: bool


@dataclass(frozen=True)
class RegisterPatientCommand:
    name: str
    cpf: str
    insurance_plan: str


class IPatientsModule(ABC):
    @abstractmethod
    def register_patient(self, cmd: RegisterPatientCommand) -> PatientDto:
        pass

    @abstractmethod
    def get_patient(self, patient_id: str) -> Optional[PatientDto]:
        pass
