"""Controlador de apresentação (Ring 4 - Infrastructure)."""

from typing import Dict, Any
from application.enrollment_service import AcademicEnrollmentApplicationService
from application.dtos import (
    EnrollStudentCommand,
    DropEnrollmentCommand,
)
from domain.model.exceptions import AcademicDomainException


class AcademicEnrollmentController:
    """Controlador que adapta chamadas de portal do aluno para comandos da aplicação."""
    def __init__(self, enrollment_service: AcademicEnrollmentApplicationService) -> None:
        self._service = enrollment_service

    def post_enroll(self, cmd: EnrollStudentCommand) -> Dict[str, Any]:
        try:
            res = self._service.enroll(cmd)
            return {
                "http_status": 201 if res.status == "CONFIRMED" else 200,
                "data": {
                    "enrollment_id": res.enrollment_id,
                    "student": res.student_name,
                    "course": res.course_title,
                    "status": res.status,
                    "credits_assigned": res.credits_assigned,
                    "total_enrolled_credits": res.current_total_credits,
                    "message": res.message,
                }
            }
        except AcademicDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "REJECTED", "error": str(e)}
            }

    def post_drop(self, cmd: DropEnrollmentCommand) -> Dict[str, Any]:
        try:
            res = self._service.drop_course(cmd)
            return {
                "http_status": 200,
                "data": {
                    "enrollment_id": res.enrollment_id,
                    "status": res.status,
                    "credits_released": res.credits_released,
                    "total_enrolled_credits": res.current_total_credits,
                    "message": res.message,
                }
            }
        except AcademicDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "ERROR", "error": str(e)}
            }
