"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional


@dataclass(frozen=True)
class Question:
    question_id: str
    prompt: str
    weight: float
    correct_choice: str  # "A", "B", "C", "D"


@dataclass(frozen=True)
class Student:
    student_id: str
    name: str
    email: str


@dataclass
class Exam:
    exam_id: str
    title: str
    min_passing_percent: float  # Ex: 70.0
    questions: List[Question]

    def evaluate_submission(self, student_answers: Dict[str, str]) -> Tuple[float, float, float, bool]:
        """
        Regra Corporativa de Negócio:
        Calcula a soma das pontuações ponderadas, o percentual de acerto e a aprovação.
        Retorna: (pontos_obtidos, pontos_maximos, percentual, aprovado).
        """
        total_weight = sum(q.weight for q in self.questions)
        if total_weight <= 0:
            return 0.0, 0.0, 0.0, False

        score_obtained = 0.0
        for q in self.questions:
            student_choice = student_answers.get(q.question_id, "").strip().upper()
            if student_choice == q.correct_choice.upper():
                score_obtained += q.weight

        percentage = round((score_obtained / total_weight) * 100.0, 2)
        is_passed = percentage >= self.min_passing_percent
        return score_obtained, total_weight, percentage, is_passed


@dataclass(frozen=True)
class Certificate:
    certificate_id: str
    student_id: str
    student_name: str
    exam_id: str
    exam_title: str
    score_percent: float
    issued_at: datetime
