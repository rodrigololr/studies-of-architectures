"""Ponto de Entrada e Facade do Módulo Identity."""

import uuid
from typing import Optional
from shared.events import InProcessEventBus
from modules.identity.public_contracts import (
    IIdentityModule,
    RegisterTenantCommand,
    TenantDto,
    TenantRegisteredDomainEvent,
)
from modules.identity.internal.identity_internal import (
    _InternalTenant,
    _InternalIdentityRepository,
)


class IdentityModule(IIdentityModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalIdentityRepository()

    def register_tenant(self, cmd: RegisterTenantCommand) -> TenantDto:
        tenant_id = f"TEN_{uuid.uuid4().hex[:8].upper()}"
        tenant = _InternalTenant(
            tenant_id=tenant_id,
            company_name=cmd.company_name,
            admin_email=cmd.admin_email,
        )
        self._repo.save(tenant)

        # Publica evento de novo tenant registrado
        self._bus.publish(TenantRegisteredDomainEvent(
            tenant_id=tenant.tenant_id,
            company_name=tenant.company_name,
            admin_email=tenant.admin_email,
            initial_plan=cmd.initial_plan,
        ))

        return TenantDto(
            tenant_id=tenant.tenant_id,
            company_name=tenant.company_name,
            admin_email=tenant.admin_email,
            is_active=tenant.is_active,
        )

    def get_tenant(self, tenant_id: str) -> Optional[TenantDto]:
        t = self._repo.find_by_id(tenant_id)
        if not t:
            return None
        return TenantDto(
            tenant_id=t.tenant_id,
            company_name=t.company_name,
            admin_email=t.admin_email,
            is_active=t.is_active,
        )
