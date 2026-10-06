"""
interface_adapters/presenters.py - Camada 3: Presenter de Avaliação de Provas.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import SubmitExamResponseModel
from use_cases.boundaries import GradeExamOutputBoundary


class ExamGradingPresenter(GradeExamOutputBoundary):
    def __init__(self) -> None:
        self.status_code: int = 200
        self.response_body: Dict[str, Any] = {}

    def present(self, response: SubmitExamResponseModel) -> None:
        if response.success:
            self.status_code = 200
            self.response_body = {
                "status": "EVALUATED",
                "result": {
                    "student": response.student_name,
                    "exam": response.exam_title,
                    "score": f"{response.score_obtained:.1f} / {response.total_points:.1f}",
                    "percentage": f"{response.score_percentage:.1f}%",
                    "approved": response.is_passed,
                    "certificate_code": response.certificate_id,
                },
                "feedback": response.message,
            }
        else:
            self.status_code = 404
            self.response_body = {
                "status": "ERROR",
                "error": response.message,
            }
