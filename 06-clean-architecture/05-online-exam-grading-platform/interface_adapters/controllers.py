"""
interface_adapters/controllers.py - Camada 3: Controller de Submissão de Provas.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import SubmitExamRequestModel
from use_cases.boundaries import GradeExamInputBoundary


class ExamSubmissionController:
    def __init__(self, grade_exam_use_case: GradeExamInputBoundary) -> None:
        self.grade_exam_use_case = grade_exam_use_case

    def handle_post_exam_submit(self, payload: Dict[str, Any]) -> None:
        req = SubmitExamRequestModel(
            exam_id=payload.get("exam_id", ""),
            student_id=payload.get("student_id", ""),
            answers=payload.get("answers", {}),
        )
        self.grade_exam_use_case.execute(req)
