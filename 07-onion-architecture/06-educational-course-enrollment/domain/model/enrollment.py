"""Entidade de Matrícula (Enrollment) e Decisão de Admissão."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class EnrollmentStatus(Enum):
    CONFIRMED = "CONFIRMED"
    WAITLISTED = "WAITLISTED"
    DROPPED = "DROPPED"


@dataclass(frozen=True)
class EnrollmentDecision:
    """Decisão calculada pelo Domain Service sobre a solicitação de matrícula."""
    is_eligible: bool
    status: EnrollmentStatus
    assigned_credits: int
    missing_prerequisites: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class Enrollment:
    """Entidade do Domínio: Vínculo de Matrícula entre Aluno e Disciplina."""
    enrollment_id: str
    student_id: str
    course_id: str
    semester: str
    credits: int
    status: EnrollmentStatus
    enrolled_at: datetime = field(default_factory=datetime.now)

    def drop(self) -> None:
        """Efetua o trancamento/cancelamento da matrícula."""
        self.status = EnrollmentStatus.DROPPED
