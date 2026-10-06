"""
report_card_controller.py - Camada de Controlador (Controller).

Orquestra o lançamento de notas por disciplina no modelo
e aciona a geração e exibição do boletim escolar formatado.
"""

from __future__ import annotations
from typing import List
from models.academic_model import StudentAcademicModel
from views.report_card_view import ReportCardView


class StudentReportController:
    def __init__(self, model: StudentAcademicModel) -> None:
        self.model = model
        self.view = ReportCardView()

    def record_subject_performance(
        self, subject: str, b1: float, b2: float, b3: float, b4: float, attendance: float
    ) -> None:
        grades = [b1, b2, b3, b4]
        self.model.add_subject_record(subject, grades, attendance)

    def print_student_report_card(self) -> None:
        records = self.model.list_records()
        overall_stats = self.model.get_overall_academic_status()
        self.view.render(
            student_name=self.model.student_name,
            enrollment_id=self.model.enrollment_id,
            records=records,
            overall_stats=overall_stats,
        )
