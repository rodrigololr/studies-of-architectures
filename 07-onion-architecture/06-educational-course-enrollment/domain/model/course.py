"""Entidade de Disciplina / Curso Universitário (Course)."""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class Course:
    """Entidade do Domínio: Disciplina acadêmica ofertada."""
    course_id: str
    code: str              # ex: "MAT101", "FIS202"
    title: str             # ex: "Cálculo Diferencial e Integral I"
    credits: int           # ex: 4 créditos
    capacity: int          # Limite de alunos matriculados
    prerequisite_ids: Set[str] = field(default_factory=set)
    enrolled_count: int = 0
    waitlist_count: int = 0

    @property
    def is_full(self) -> bool:
        """Indica se a turma atingiu o número máximo de vagas regulares."""
        return self.enrolled_count >= self.capacity

    def increment_enrolled(self) -> None:
        """Incrementa contagem de matriculados regulares."""
        self.enrolled_count += 1

    def decrement_enrolled(self) -> None:
        """Decrementa contagem de matriculados regulares."""
        if self.enrolled_count > 0:
            self.enrolled_count -= 1

    def increment_waitlist(self) -> None:
        """Incrementa contagem de alunos na fila de espera."""
        self.waitlist_count += 1
