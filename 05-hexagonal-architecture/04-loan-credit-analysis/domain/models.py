"""
models.py - Modelos de domínio da análise de crédito e risco.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List


class CreditDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RiskRating(str, Enum):
    AAA = "AAA"  # Excelente
    AA = "AA"    # Muito Bom
    A = "A"      # Bom
    B = "B"      # Regular / Alto Risco


@dataclass(frozen=True)
class Applicant:
    cpf: str
    full_name: str
    monthly_income: float
    birth_date: str


@dataclass(frozen=True)
class LoanProposal:
    proposal_id: str
    applicant: Applicant
    requested_amount: float
    installments_count: int


@dataclass(frozen=True)
class BureauScore:
    bureau_name: str
    score: int  # 0 a 1000
    has_active_defaults: bool


@dataclass(frozen=True)
class CreditAnalysisResult:
    proposal_id: str
    decision: CreditDecision
    risk_rating: RiskRating
    approved_amount: float
    monthly_installment: float
    annual_interest_rate: float
    reasons: List[str]
    analyzed_at: datetime
