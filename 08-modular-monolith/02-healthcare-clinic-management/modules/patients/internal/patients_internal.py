"""Implementação Interna do Módulo Patients."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class _InternalPatient:
    patient_id: str
    name: str
    cpf: str
    insurance_plan: str
    is_active: bool = True


class _InternalPatientRepository:
    def __init__(self) -> None:
        self._db: Dict[str, _InternalPatient] = {}

    def save(self, patient: _InternalPatient) -> None:
        self._db[patient.patient_id] = patient

    def find_by_id(self, patient_id: str) -> Optional[_InternalPatient]:
        return self._db.get(patient_id)
