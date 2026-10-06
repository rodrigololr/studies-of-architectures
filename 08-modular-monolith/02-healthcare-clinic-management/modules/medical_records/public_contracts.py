"""Contrato Público do Módulo Medical Records (Prontuário Médico Eletrônico)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class CreateMedicalRecordCommand:
    appointment_id: str
    patient_id: str
    doctor_crm: str
    anamnesis: str
    icd10_diagnosis: str  # ex: "J06.9" (Infecção respiratória aguda)
    prescription: str


@dataclass(frozen=True)
class MedicalRecordDto:
    record_id: str
    appointment_id: str
    patient_id: str
    doctor_crm: str
    anamnesis: str
    icd10_diagnosis: str
    prescription: str
    recorded_at: datetime


class IMedicalRecordsModule(ABC):
    @abstractmethod
    def add_record(self, cmd: CreateMedicalRecordCommand, requester_crm: str) -> MedicalRecordDto:
        """Adiciona prontuário médico. Exige que o solicitante seja o médico com CRM válido."""
        pass

    @abstractmethod
    def get_patient_history(self, patient_id: str, requester_crm: str) -> List[MedicalRecordDto]:
        """Consulta histórico médico. Acesso restrito por sigilo profissional."""
        pass
