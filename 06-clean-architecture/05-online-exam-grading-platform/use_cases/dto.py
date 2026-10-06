"""
use_cases/dto.py - Camada 2: DTOs para Submissão e Correção de Provas.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class SubmitExamRequestModel:
    exam_id: str
    student_id: str
    answers: Dict[str, str]  # question_id -> alternative ("A", "B", etc.)


@dataclass(frozen=True)
class SubmitExamResponseModel:
    success: bool
    student_name: Optional[str]
    exam_title: Optional[str]
    score_obtained: float
    total_points: float
    score_percentage: float
    is_passed: bool
    certificate_id: Optional[str]
    message: str
