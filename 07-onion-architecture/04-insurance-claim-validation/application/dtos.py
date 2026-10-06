"""Data Transfer Objects (DTOs) da camada de aplicação."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class SubmitClaimCommand:
    """Comando para registro de aviso de sinistro."""
    policy_id: str
    insured_name: str
    occurrence_date: datetime
    claimed_amount: float
    description: str


@dataclass(frozen=True)
class SubmitClaimResponse:
    """Resultado da abertura de sinistro."""
    claim_id: str
    status: str
    message: str


@dataclass(frozen=True)
class AssessClaimCommand:
    """Comando para registro do laudo pericial e regulação."""
    claim_id: str
    assessor_id: str
    loss_cause: str
    estimated_repair_cost: float
    damaged_items: List[str]
    is_total_loss: bool
    evidence_urls: List[str]


@dataclass(frozen=True)
class SettleClaimResponse:
    """Resultado da regulação e decisão do sinistro."""
    claim_id: str
    status: str
    approved: bool
    gross_loss: float
    deductible_applied: float
    payable_amount: float
    justification: str
