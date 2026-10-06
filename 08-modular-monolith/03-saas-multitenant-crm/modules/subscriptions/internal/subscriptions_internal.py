"""Implementação Interna do Módulo Subscriptions (Schema: subscriptions)."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class _PlanTier:
    name: str
    max_leads: int
    price: float


PLAN_CATALOG = {
    "STARTER": _PlanTier("STARTER", max_leads=3, price=49.0),
    "PRO": _PlanTier("PRO", max_leads=10, price=149.0),
    "ENTERPRISE": _PlanTier("ENTERPRISE", max_leads=999999, price=499.0),
}


@dataclass
class _InternalSubscription:
    tenant_id: str
    plan_name: str
    is_active: bool = True


class _InternalSubscriptionRepository:
    def __init__(self) -> None:
        self._subs: Dict[str, _InternalSubscription] = {}

    def save(self, sub: _InternalSubscription) -> None:
        self._subs[sub.tenant_id] = sub

    def find_by_tenant(self, tenant_id: str) -> Optional[_InternalSubscription]:
        return self._subs.get(tenant_id)
