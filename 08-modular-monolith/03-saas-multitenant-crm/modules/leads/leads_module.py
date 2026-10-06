"""Ponto de Entrada e Facade do Módulo Leads."""

import uuid
from typing import List
from shared.events import InProcessEventBus
from modules.identity.public_contracts import IIdentityModule
from modules.subscriptions.public_contracts import ISubscriptionModule
from modules.leads.public_contracts import (
    ILeadsModule,
    CreateLeadCommand,
    LeadDto,
    LeadCreatedDomainEvent,
    QuotaExceededError,
)
from modules.leads.internal.leads_internal import (
    _InternalLead,
    _InternalLeadRepository,
)


class LeadsModule(ILeadsModule):
    def __init__(
        self,
        identity_module: IIdentityModule,
        subscriptions_module: ISubscriptionModule,
        event_bus: InProcessEventBus,
    ) -> None:
        self._identity = identity_module
        self._subs = subscriptions_module
        self._bus = event_bus
        self._repo = _InternalLeadRepository()

    def create_lead(self, cmd: CreateLeadCommand) -> LeadDto:
        tenant = self._identity.get_tenant(cmd.tenant_id)
        if not tenant or not tenant.is_active:
            raise ValueError(f"Tenant '{cmd.tenant_id}' não existe ou está inativo.")

        # Valida cota máxima permitida pelo módulo de assinaturas
        current_count = self._repo.count_by_tenant(cmd.tenant_id)
        if not self._subs.can_create_lead(cmd.tenant_id, current_count):
            limits = self._subs.get_plan_limits(cmd.tenant_id)
            raise QuotaExceededError(
                f"Limite de leads atingido para o plano '{limits.plan_name}' ({current_count}/{limits.max_leads}). "
                "Faça upgrade de plano para cadastrar mais leads."
            )

        lead_id = f"LED_{uuid.uuid4().hex[:8].upper()}"
        internal_lead = _InternalLead(
            lead_id=lead_id,
            tenant_id=cmd.tenant_id,
            contact_name=cmd.contact_name,
            contact_email=cmd.contact_email,
            estimated_value=cmd.estimated_value,
        )
        self._repo.save(internal_lead)

        # Dispara evento para o módulo de auditoria
        self._bus.publish(LeadCreatedDomainEvent(
            tenant_id=internal_lead.tenant_id,
            lead_id=internal_lead.lead_id,
            contact_name=internal_lead.contact_name,
            estimated_value=internal_lead.estimated_value,
        ))

        return LeadDto(
            lead_id=internal_lead.lead_id,
            tenant_id=internal_lead.tenant_id,
            contact_name=internal_lead.contact_name,
            contact_email=internal_lead.contact_email,
            estimated_value=internal_lead.estimated_value,
            status=internal_lead.status,
        )

    def list_leads(self, tenant_id: str) -> List[LeadDto]:
        return [
            LeadDto(
                lead_id=l.lead_id,
                tenant_id=l.tenant_id,
                contact_name=l.contact_name,
                contact_email=l.contact_email,
                estimated_value=l.estimated_value,
                status=l.status,
            )
            for l in self._repo.list_by_tenant(tenant_id)
        ]

    def count_leads(self, tenant_id: str) -> int:
        return self._repo.count_by_tenant(tenant_id)
