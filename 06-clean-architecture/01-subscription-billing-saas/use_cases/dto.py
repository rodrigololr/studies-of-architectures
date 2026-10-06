"""
use_cases/dto.py - Camada 2: Data Transfer Objects (Request & Response Models).

Objetos puros de transferência de dados que cruzam as fronteiras dos Casos de Uso.
Nunca expõem diretamente instâncias de banco de dados nem bibliotecas de formulários.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateSubscriptionRequestModel:
    customer_id: str
    plan_id: str
    cycle: str  # "MONTHLY" | "ANNUALLY"


@dataclass(frozen=True)
class CreateSubscriptionResponseModel:
    success: bool
    subscription_id: Optional[str]
    customer_name: Optional[str]
    plan_name: Optional[str]
    cycle: Optional[str]
    amount_charged: float
    next_billing_date: Optional[str]
    message: str


@dataclass(frozen=True)
class UpgradePlanRequestModel:
    subscription_id: str
    new_plan_id: str


@dataclass(frozen=True)
class UpgradePlanResponseModel:
    success: bool
    subscription_id: Optional[str]
    old_plan_name: Optional[str]
    new_plan_name: Optional[str]
    unused_credit: float
    prorated_amount_charged: float
    message: str


@dataclass(frozen=True)
class CancelSubscriptionRequestModel:
    subscription_id: str
    reason: str


@dataclass(frozen=True)
class CancelSubscriptionResponseModel:
    success: bool
    subscription_id: Optional[str]
    cancelled_at: Optional[str]
    message: str
