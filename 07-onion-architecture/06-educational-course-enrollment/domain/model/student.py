"""Entidade de Aluno Universitário (Student)."""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class Student:
    """Entidade do Domínio: Aluno com histórico escolar e carga horária atual."""
    student_id: str
    name: str
    registration_number: str
    max_semester_credits: int = 24
    current_enrolled_credits: int = 0
    completed_course_ids: Set[str] = field(default_factory=set)

    def has_completed(self, course_id: str) -> bool:
        """Verifica se o aluno já foi aprovado na disciplina indicada."""
        return course_id in self.completed_course_ids

    def can_add_credits(self, credits_to_add: int) -> bool:
        """Garante a invariante de limite de carga horária semestral."""
        return (self.current_enrolled_credits + credits_to_add) <= self.max_semester_credits

    def add_credits(self, credits: int) -> None:
        self.current_enrolled_credits += credits

    def remove_credits(self, credits: int) -> None:
        self.current_enrolled_credits = max(0, self.current_enrolled_credits - credits)
