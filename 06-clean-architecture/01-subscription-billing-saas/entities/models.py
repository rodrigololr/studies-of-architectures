"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).

Entidades e Value Objects puros com suas regras críticas de negócio corporativo.
Zero dependência de frameworks, bancos de dados, bibliotecas de UI ou gateways.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import List, Optional


class BillingCycle(str, Enum):
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Plan:
    plan_id: str
    name: str
    monthly_price: float
    annual_price: float
    max_seats: int
    features: List[str]

    def get_price_for_cycle(self, cycle: BillingCycle) -> float:
        if cycle == BillingCycle.ANNUALLY:
            return self.annual_price
        return self.monthly_price


@dataclass(frozen=True)
class Customer:
    customer_id: str
    name: str
    email: str
    payment_method_token: str


@dataclass
class Subscription:
    subscription_id: str
    customer_id: str
    plan: Plan
    cycle: BillingCycle
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancellation_date: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

    def calculate_proration_credit(
        self,
        new_plan: Plan,
        now: datetime,
    ) -> tuple[float, float, float]:
        """
        Regra Corporativa de Negócio:
        Calcula o crédito proporcional dos dias não utilizados do plano atual
        e calcula a diferença a ser faturada para o novo plano (Proration).
        Retorna (credito_nao_usado, valor_novo_plano, total_a_pagar).
        """
        if now >= self.current_period_end:
            # Período já expirado, sem crédito
            return 0.0, new_plan.get_price_for_cycle(self.cycle), new_plan.get_price_for_cycle(self.cycle)

        total_seconds = (self.current_period_end - self.current_period_start).total_seconds()
        remaining_seconds = (self.current_period_end - now).total_seconds()
        fraction_remaining = max(0.0, min(1.0, remaining_seconds / total_seconds))

        current_price = self.plan.get_price_for_cycle(self.cycle)
        unused_credit = round(current_price * fraction_remaining, 2)

        new_plan_price = new_plan.get_price_for_cycle(self.cycle)
        net_to_charge = round(max(0.0, new_plan_price - unused_credit), 2)

        return unused_credit, new_plan_price, net_to_charge

    def upgrade_plan(self, new_plan: Plan, now: datetime) -> None:
        """Aplica o upgrade na assinatura."""
        self.plan = new_plan
        self.status = SubscriptionStatus.ACTIVE

    def cancel(self, now: datetime) -> None:
        """Inativa a assinatura."""
        self.status = SubscriptionStatus.CANCELLED
        self.cancellation_date = now
