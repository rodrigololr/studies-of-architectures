"""Contrato Público do Módulo Performance (Avaliação de Desempenho e Metas)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SubmitReviewCommand:
    employee_id: str
    reviewer_name: str
    score: float  # 0.0 a 100.0
    feedback: str


@dataclass(frozen=True)
class PerformanceReviewDto:
    review_id: str
    employee_id: str
    reviewer_name: str
    score: float
    rating: str  # "EXCEEDS_EXPECTATIONS", "MEETS_EXPECTATIONS", "NEEDS_IMPROVEMENT"
    feedback: str


class IPerformanceModule(ABC):
    @abstractmethod
    def submit_review(self, cmd: SubmitReviewCommand) -> PerformanceReviewDto:
        pass

    @abstractmethod
    def get_reviews_for_employee(self, employee_id: str) -> List[PerformanceReviewDto]:
        pass
