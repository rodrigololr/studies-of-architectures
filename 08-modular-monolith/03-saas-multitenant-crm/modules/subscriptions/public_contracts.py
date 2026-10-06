"""Contrato Público do Módulo Subscriptions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from shared.events import DomainEvent


@dataclass(frozen=True)
class PlanLimitsDto:
    tenant_id: str
    plan_name: str
    max_leads: int
    monthly_price: float
    is_active: bool


@dataclass(frozen=True)
class ChangePlanCommand:
    tenant_id: str
    new_plan: str  # "STARTER", "PRO", "ENTERPRISE"


@dataclass(frozen=True)
class PlanChangedDomainEvent(DomainEvent):
    old_plan: str = ""
    new_plan: str = ""


class ISubscriptionModule(ABC):
    @abstractmethod
    def get_plan_limits(self, tenant_id: str) -> PlanLimitsDto:
        pass

    @abstractmethod
    def can_create_lead(self, tenant_id: str, current_lead_count: int) -> bool:
        pass

    @abstractmethod
    def change_plan(self, cmd: ChangePlanCommand) -> PlanLimitsDto:
        pass
