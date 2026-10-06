"""
academic_model.py - Camada de Modelo (Model).

Modelos para controle de notas bimestrais, cálculo de médias aritméticas,
avaliação de presença escolar e regras estatutárias de aprovação.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class AcademicStatus(str, Enum):
    APPROVED = "APROVADO"
    RECOVERY = "RECUPERAÇÃO"
    FAILED_BY_GRADE = "REPROVADO POR NOTA"
    FAILED_BY_ABSENCE = "REPROVADO POR FALTA"


@dataclass
class SubjectRecord:
    subject_name: str
    grades: List[float]       # Até 4 notas bimestrais
    attendance_pct: float     # Frequência de 0 a 100%

    @property
    def final_average(self) -> float:
        return round(sum(self.grades) / len(self.grades), 1) if self.grades else 0.0

    @property
    def status(self) -> AcademicStatus:
        # Regra 1: Frequência mínima obrigatória de 75%
        if self.attendance_pct < 75.0:
            return AcademicStatus.FAILED_BY_ABSENCE

        avg = self.final_average
        # Regra 2: Média para aprovação direta >= 7.0
        if avg >= 7.0:
            return AcademicStatus.APPROVED
        # Regra 3: Recuperação entre 5.0 e 6.9
        elif avg >= 5.0:
            return AcademicStatus.RECOVERY
        else:
            return AcademicStatus.FAILED_BY_GRADE


class StudentAcademicModel:
    def __init__(self, student_name: str, enrollment_id: str) -> None:
        self.student_name = student_name
        self.enrollment_id = enrollment_id
        self._subjects: Dict[str, SubjectRecord] = {}

    def add_subject_record(self, subject_name: str, grades: List[float], attendance_pct: float) -> SubjectRecord:
        if len(grades) != 4:
            raise ValueError("Devem ser fornecidas exatamente 4 notas bimestrais.")
        for g in grades:
            if not (0.0 <= g <= 10.0):
                raise ValueError(f"Nota inválida: {g}. As notas devem estar entre 0.0 e 10.0.")

        if not (0.0 <= attendance_pct <= 100.0):
            raise ValueError("Frequência deve estar entre 0% e 100%.")

        record = SubjectRecord(
            subject_name=subject_name.strip(),
            grades=grades,
            attendance_pct=round(attendance_pct, 1),
        )
        self._subjects[subject_name] = record
        return record

    def list_records(self) -> List[SubjectRecord]:
        return list(self._subjects.values())

    def get_overall_academic_status(self) -> Tuple[float, str]:
        records = list(self._subjects.values())
        if not records:
            return 0.0, "SEM DISCIPLINAS"

        overall_avg = round(sum(r.final_average for r in records) / len(records), 1)
        has_failure = any(r.status in (AcademicStatus.FAILED_BY_GRADE, AcademicStatus.FAILED_BY_ABSENCE) for r in records)
        has_recovery = any(r.status == AcademicStatus.RECOVERY for r in records)

        if has_failure:
            overall_status = "REPROVADO NO ANO LETIVO"
        elif has_recovery:
            overall_status = "EM RECUPERAÇÃO FINAL"
        else:
            overall_status = "APROVADO DE ANO"

        return overall_avg, overall_status
