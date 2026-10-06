"""Ponto de Entrada e Facade do Módulo Patients."""

import uuid
from typing import Optional
from modules.patients.public_contracts import (
    IPatientsModule,
    PatientDto,
    RegisterPatientCommand,
)
from modules.patients.internal.patients_internal import (
    _InternalPatient,
    _InternalPatientRepository,
)


class PatientsModule(IPatientsModule):
    def __init__(self) -> None:
        self._repo = _InternalPatientRepository()

    def register_patient(self, cmd: RegisterPatientCommand) -> PatientDto:
        patient_id = f"PAT_{uuid.uuid4().hex[:8].upper()}"
        patient = _InternalPatient(
            patient_id=patient_id,
            name=cmd.name,
            cpf=cmd.cpf,
            insurance_plan=cmd.insurance_plan,
        )
        self._repo.save(patient)
        return PatientDto(
            patient_id=patient.patient_id,
            name=patient.name,
            cpf=patient.cpf,
            insurance_plan=patient.insurance_plan,
            is_active=patient.is_active,
        )

    def get_patient(self, patient_id: str) -> Optional[PatientDto]:
        p = self._repo.find_by_id(patient_id)
        if not p:
            return None
        return PatientDto(
            patient_id=p.patient_id,
            name=p.name,
            cpf=p.cpf,
            insurance_plan=p.insurance_plan,
            is_active=p.is_active,
        )
