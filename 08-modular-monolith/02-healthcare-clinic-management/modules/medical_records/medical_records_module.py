"""Ponto de Entrada e Facade do Módulo Medical Records."""

import uuid
from typing import List
from modules.medical_records.public_contracts import (
    IMedicalRecordsModule,
    CreateMedicalRecordCommand,
    MedicalRecordDto,
)
from modules.medical_records.internal.medical_records_internal import (
    _InternalMedicalRecord,
    _InternalMedicalRecordRepository,
)


class MedicalRecordsModule(IMedicalRecordsModule):
    """Facade pública do módulo Medical Records."""
    def __init__(self) -> None:
        self._repo = _InternalMedicalRecordRepository()

    def add_record(self, cmd: CreateMedicalRecordCommand, requester_crm: str) -> MedicalRecordDto:
        # Validação estrita de autorização por CRM médico
        if not requester_crm or requester_crm.strip() != cmd.doctor_crm.strip():
            raise PermissionError(
                f"Violação de Sigilo Médico / LGPD: Apenas o médico titular ({cmd.doctor_crm}) pode registrar no prontuário."
            )

        rec_id = f"REC_{uuid.uuid4().hex[:8].upper()}"
        internal_rec = _InternalMedicalRecord(
            record_id=rec_id,
            appointment_id=cmd.appointment_id,
            patient_id=cmd.patient_id,
            doctor_crm=cmd.doctor_crm,
            anamnesis=cmd.anamnesis,
            icd10_diagnosis=cmd.icd10_diagnosis,
            prescription=cmd.prescription,
        )
        self._repo.save(internal_rec)

        return MedicalRecordDto(
            record_id=internal_rec.record_id,
            appointment_id=internal_rec.appointment_id,
            patient_id=internal_rec.patient_id,
            doctor_crm=internal_rec.doctor_crm,
            anamnesis=internal_rec.anamnesis,
            icd10_diagnosis=internal_rec.icd10_diagnosis,
            prescription=internal_rec.prescription,
            recorded_at=internal_rec.recorded_at,
        )

    def get_patient_history(self, patient_id: str, requester_crm: str) -> List[MedicalRecordDto]:
        if not requester_crm or not requester_crm.startswith("CRM/"):
            raise PermissionError("Acesso negado: Visualização de prontuários requer credencial de CRM médico ativo.")

        records = self._repo.list_by_patient(patient_id)
        return [
            MedicalRecordDto(
                record_id=r.record_id,
                appointment_id=r.appointment_id,
                patient_id=r.patient_id,
                doctor_crm=r.doctor_crm,
                anamnesis=r.anamnesis,
                icd10_diagnosis=r.icd10_diagnosis,
                prescription=r.prescription,
                recorded_at=r.recorded_at,
            )
            for r in records
        ]
