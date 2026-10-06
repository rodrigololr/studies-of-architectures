"""Implementação Interna do Módulo Performance (Schema: performance)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class _InternalReview:
    review_id: str
    employee_id: str
    reviewer_name: str
    score: float
    rating: str
    feedback: str
    reviewed_at: datetime = field(default_factory=datetime.now)


class _InternalPerformanceRepository:
    def __init__(self) -> None:
        self._reviews: Dict[str, _InternalReview] = {}

    def save(self, rev: _InternalReview) -> None:
        self._reviews[rev.review_id] = rev

    def list_by_employee(self, employee_id: str) -> List[_InternalReview]:
        return [r for r in self._reviews.values() if r.employee_id == employee_id]
