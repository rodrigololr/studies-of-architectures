"""Implementação Interna Privada do Módulo Medical Records (Schema: medical_records)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class _InternalMedicalRecord:
    record_id: str
    appointment_id: str
    patient_id: str
    doctor_crm: str
    anamnesis: str
    icd10_diagnosis: str
    prescription: str
    recorded_at: datetime = field(default_factory=datetime.now)


class _InternalMedicalRecordRepository:
    def __init__(self) -> None:
        self._records: Dict[str, _InternalMedicalRecord] = {}

    def save(self, record: _InternalMedicalRecord) -> None:
        self._records[record.record_id] = record

    def list_by_patient(self, patient_id: str) -> List[_InternalMedicalRecord]:
        return [r for r in self._records.values() if r.patient_id == patient_id]
