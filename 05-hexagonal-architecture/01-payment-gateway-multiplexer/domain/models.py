"""
models.py - Núcleo de Domínio (Domain).
Entidades e Value Objects puros do domínio de pagamentos, sem acoplamento a gateways específicos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class PaymentRequest:
    payment_id: str
    amount: float
    customer_email: str
    credit_card_token: str
    currency: str = "BRL"


@dataclass(frozen=True)
class PaymentResponse:
    payment_id: str
    amount: float
    currency: str
    status: PaymentStatus
    provider_used: str
    processed_at: datetime
    transaction_id: Optional[str] = None
    fee_charged: float = 0.0
    error_message: Optional[str] = None
