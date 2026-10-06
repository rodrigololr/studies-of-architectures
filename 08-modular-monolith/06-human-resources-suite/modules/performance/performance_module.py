"""Ponto de Entrada e Facade do Módulo Performance."""

import uuid
from typing import List
from modules.performance.public_contracts import (
    IPerformanceModule,
    SubmitReviewCommand,
    PerformanceReviewDto,
)
from modules.performance.internal.performance_internal import (
    _InternalReview,
    _InternalPerformanceRepository,
)


class PerformanceModule(IPerformanceModule):
    def __init__(self) -> None:
        self._repo = _InternalPerformanceRepository()

    def submit_review(self, cmd: SubmitReviewCommand) -> PerformanceReviewDto:
        if cmd.score >= 90.0:
            rating = "EXCEEDS_EXPECTATIONS"
        elif cmd.score >= 70.0:
            rating = "MEETS_EXPECTATIONS"
        else:
            rating = "NEEDS_IMPROVEMENT"

        rev_id = f"REV_{uuid.uuid4().hex[:8].upper()}"
        rev = _InternalReview(
            review_id=rev_id,
            employee_id=cmd.employee_id,
            reviewer_name=cmd.reviewer_name,
            score=cmd.score,
            rating=rating,
            feedback=cmd.feedback,
        )
        self._repo.save(rev)

        return PerformanceReviewDto(
            review_id=rev.review_id,
            employee_id=rev.employee_id,
            reviewer_name=rev.reviewer_name,
            score=rev.score,
            rating=rev.rating,
            feedback=rev.feedback,
        )

    def get_reviews_for_employee(self, employee_id: str) -> List[PerformanceReviewDto]:
        return [
            PerformanceReviewDto(
                review_id=r.review_id,
                employee_id=r.employee_id,
                reviewer_name=r.reviewer_name,
                score=r.score,
                rating=r.rating,
                feedback=r.feedback,
            )
            for r in self._repo.list_by_employee(employee_id)
        ]
