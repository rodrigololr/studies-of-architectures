"""Data Transfer Objects (DTOs) da aplicação acadêmica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EnrollStudentCommand:
    """Comando para requisição de matrícula."""
    student_id: str
    course_id: str
    semester: str


@dataclass(frozen=True)
class EnrollStudentResponseDto:
    """Resultado da tentativa de matrícula."""
    enrollment_id: str
    student_name: str
    course_title: str
    status: str
    credits_assigned: int
    current_total_credits: int
    message: str


@dataclass(frozen=True)
class DropEnrollmentCommand:
    """Comando para cancelamento/trancamento de disciplina."""
    enrollment_id: str


@dataclass(frozen=True)
class DropEnrollmentResponseDto:
    """Resultado do trancamento de matrícula."""
    enrollment_id: str
    status: str
    credits_released: int
    current_total_credits: int
    message: str
