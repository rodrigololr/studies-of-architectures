"""Ponto de Entrada e Facade do Módulo Subscriptions."""

from shared.events import InProcessEventBus
from modules.identity.public_contracts import TenantRegisteredDomainEvent
from modules.subscriptions.public_contracts import (
    ISubscriptionModule,
    PlanLimitsDto,
    ChangePlanCommand,
    PlanChangedDomainEvent,
)
from modules.subscriptions.internal.subscriptions_internal import (
    _InternalSubscription,
    _InternalSubscriptionRepository,
    PLAN_CATALOG,
)


class SubscriptionsModule(ISubscriptionModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalSubscriptionRepository()

        # Reage à criação de novo tenant para inicializar a assinatura correspondente
        self._bus.subscribe(TenantRegisteredDomainEvent, self._on_tenant_registered)

    def _on_tenant_registered(self, event: TenantRegisteredDomainEvent) -> None:
        plan = event.initial_plan.upper() if event.initial_plan.upper() in PLAN_CATALOG else "STARTER"
        sub = _InternalSubscription(tenant_id=event.tenant_id, plan_name=plan)
        self._repo.save(sub)

    def get_plan_limits(self, tenant_id: str) -> PlanLimitsDto:
        sub = self._repo.find_by_tenant(tenant_id)
        plan_name = sub.plan_name if sub else "STARTER"
        tier = PLAN_CATALOG.get(plan_name, PLAN_CATALOG["STARTER"])
        return PlanLimitsDto(
            tenant_id=tenant_id,
            plan_name=tier.name,
            max_leads=tier.max_leads,
            monthly_price=tier.price,
            is_active=sub.is_active if sub else True,
        )

    def can_create_lead(self, tenant_id: str, current_lead_count: int) -> bool:
        limits = self.get_plan_limits(tenant_id)
        return current_lead_count < limits.max_leads

    def change_plan(self, cmd: ChangePlanCommand) -> PlanLimitsDto:
        new_plan = cmd.new_plan.upper()
        if new_plan not in PLAN_CATALOG:
            raise ValueError(f"Plano '{cmd.new_plan}' inválido. Disponíveis: {list(PLAN_CATALOG.keys())}")

        sub = self._repo.find_by_tenant(cmd.tenant_id)
        old_plan = sub.plan_name if sub else "STARTER"
        if not sub:
            sub = _InternalSubscription(tenant_id=cmd.tenant_id, plan_name=new_plan)
        else:
            sub.plan_name = new_plan

        self._repo.save(sub)

        # Emite evento de mudança de plano
        self._bus.publish(PlanChangedDomainEvent(
            tenant_id=cmd.tenant_id,
            old_plan=old_plan,
            new_plan=new_plan,
        ))

        tier = PLAN_CATALOG[new_plan]
        return PlanLimitsDto(
            tenant_id=cmd.tenant_id,
            plan_name=tier.name,
            max_leads=tier.max_leads,
            monthly_price=tier.price,
            is_active=sub.is_active,
        )
