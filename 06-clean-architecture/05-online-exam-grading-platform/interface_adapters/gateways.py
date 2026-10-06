"""
interface_adapters/gateways.py - Camada 3: Gateways e Repositórios de Provas.
"""

from __future__ import annotations
from typing import Dict, Optional
from entities.models import Exam, Student, Certificate
from use_cases.boundaries import (
    ExamRepositoryGateway,
    StudentRepositoryGateway,
    CertificateRepositoryGateway,
)


class InMemoryExamRepository(ExamRepositoryGateway):
    def __init__(self, exams: Optional[Dict[str, Exam]] = None) -> None:
        self._exams: Dict[str, Exam] = dict(exams or {})

    def find_by_id(self, exam_id: str) -> Optional[Exam]:
        return self._exams.get(exam_id)


class InMemoryStudentRepository(StudentRepositoryGateway):
    def __init__(self, students: Optional[Dict[str, Student]] = None) -> None:
        self._students: Dict[str, Student] = dict(students or {})

    def find_by_id(self, student_id: str) -> Optional[Student]:
        return self._students.get(student_id)


class InMemoryCertificateRepository(CertificateRepositoryGateway):
    def __init__(self) -> None:
        self._certificates: Dict[str, Certificate] = {}

    def save(self, certificate: Certificate) -> None:
        self._certificates[certificate.certificate_id] = certificate

    def find_by_id(self, certificate_id: str) -> Optional[Certificate]:
        return self._certificates.get(certificate_id)
