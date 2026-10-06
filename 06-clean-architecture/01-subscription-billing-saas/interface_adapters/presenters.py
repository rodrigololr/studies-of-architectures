"""
interface_adapters/presenters.py - Camada 3: Interface Adapters (Presenters).

Implementam os Output Boundaries dos casos de uso, formatando os Response Models
em estruturas adequadas para o cliente (JSON REST, ViewModel, CLI).
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from use_cases.dto import (
    CreateSubscriptionResponseModel,
    UpgradePlanResponseModel,
    CancelSubscriptionResponseModel,
)
from use_cases.boundaries import (
    CreateSubscriptionOutputBoundary,
    UpgradePlanOutputBoundary,
    CancelSubscriptionOutputBoundary,
)


class SubscriptionRestPresenter(
    CreateSubscriptionOutputBoundary,
    UpgradePlanOutputBoundary,
    CancelSubscriptionOutputBoundary,
):
    def __init__(self) -> None:
        self.last_status_code: int = 200
        self.last_response_data: Dict[str, Any] = {}

    def present(self, response: Any) -> None:
        if isinstance(response, CreateSubscriptionResponseModel):
            self._present_create(response)
        elif isinstance(response, UpgradePlanResponseModel):
            self._present_upgrade(response)
        elif isinstance(response, CancelSubscriptionResponseModel):
            self._present_cancel(response)

    def _present_create(self, res: CreateSubscriptionResponseModel) -> None:
        if res.success:
            self.last_status_code = 201
            self.last_response_data = {
                "success": True,
                "data": {
                    "subscription_id": res.subscription_id,
                    "customer": res.customer_name,
                    "plan": res.plan_name,
                    "cycle": res.cycle,
                    "charged_amount": res.amount_charged,
                    "renews_at": res.next_billing_date,
                },
                "message": res.message,
            }
        else:
            self.last_status_code = 400
            self.last_response_data = {
                "success": False,
                "error": res.message,
            }

    def _present_upgrade(self, res: UpgradePlanResponseModel) -> None:
        if res.success:
            self.last_status_code = 200
            self.last_response_data = {
                "success": True,
                "data": {
                    "subscription_id": res.subscription_id,
                    "old_plan": res.old_plan_name,
                    "new_plan": res.new_plan_name,
                    "unused_credit_applied": res.unused_credit,
                    "net_amount_charged": res.prorated_amount_charged,
                },
                "message": res.message,
            }
        else:
            self.last_status_code = 400
            self.last_response_data = {
                "success": False,
                "error": res.message,
            }

    def _present_cancel(self, res: CancelSubscriptionResponseModel) -> None:
        if res.success:
            self.last_status_code = 200
            self.last_response_data = {
                "success": True,
                "data": {
                    "subscription_id": res.subscription_id,
                    "cancelled_at": res.cancelled_at,
                },
                "message": res.message,
            }
        else:
            self.last_status_code = 400
            self.last_response_data = {
                "success": False,
                "error": res.message,
            }
