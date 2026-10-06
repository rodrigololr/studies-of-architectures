"""
interface_adapters/controllers.py - Camada 3: Interface Adapters (Controllers).

Recebem dados externos brutos (HTTP JSON, formulários, rotas) e convertem
para os Request Models específicos dos Input Boundaries dos casos de uso.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import (
    CreateSubscriptionRequestModel,
    UpgradePlanRequestModel,
    CancelSubscriptionRequestModel,
)
from use_cases.boundaries import (
    CreateSubscriptionInputBoundary,
    UpgradePlanInputBoundary,
    CancelSubscriptionInputBoundary,
)


class SubscriptionWebController:
    def __init__(
        self,
        create_use_case: CreateSubscriptionInputBoundary,
        upgrade_use_case: UpgradePlanInputBoundary,
        cancel_use_case: CancelSubscriptionInputBoundary,
    ) -> None:
        self.create_use_case = create_use_case
        self.upgrade_use_case = upgrade_use_case
        self.cancel_use_case = cancel_use_case

    def post_subscribe(self, payload: Dict[str, Any]) -> None:
        request_model = CreateSubscriptionRequestModel(
            customer_id=payload.get("customer_id", ""),
            plan_id=payload.get("plan_id", ""),
            cycle=payload.get("billing_cycle", "MONTHLY"),
        )
        self.create_use_case.execute(request_model)

    def put_upgrade(self, payload: Dict[str, Any]) -> None:
        request_model = UpgradePlanRequestModel(
            subscription_id=payload.get("subscription_id", ""),
            new_plan_id=payload.get("new_plan_id", ""),
        )
        self.upgrade_use_case.execute(request_model)

    def post_cancel(self, payload: Dict[str, Any]) -> None:
        request_model = CancelSubscriptionRequestModel(
            subscription_id=payload.get("subscription_id", ""),
            reason=payload.get("reason", "Solicitação do usuário"),
        )
        self.cancel_use_case.execute(request_model)
