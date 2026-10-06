"""
use_cases/boundaries.py - Camada 2: Boundaries e Gateways de Provas.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from entities.models import Exam, Student, Certificate
from use_cases.dto import SubmitExamRequestModel, SubmitExamResponseModel


class GradeExamInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: SubmitExamRequestModel) -> None:
        pass


class GradeExamOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: SubmitExamResponseModel) -> None:
        pass


class ExamRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, exam_id: str) -> Optional[Exam]:
        pass


class StudentRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, student_id: str) -> Optional[Student]:
        pass


class CertificateRepositoryGateway(ABC):
    @abstractmethod
    def save(self, certificate: Certificate) -> None:
        pass

    @abstractmethod
    def find_by_id(self, certificate_id: str) -> Optional[Certificate]:
        pass
