"""Ponto de Entrada e Facade do Módulo Audit."""

import uuid
from typing import List
from shared.events import InProcessEventBus
from modules.identity.public_contracts import TenantRegisteredDomainEvent
from modules.subscriptions.public_contracts import PlanChangedDomainEvent
from modules.leads.public_contracts import LeadCreatedDomainEvent
from modules.audit.public_contracts import IAuditModule, AuditEntryDto
from modules.audit.internal.audit_internal import _InternalAuditLog, _InternalAuditRepository


class AuditModule(IAuditModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalAuditRepository()

        # Inscrição para escutar todos os eventos do ecossistema do monólito
        self._bus.subscribe(TenantRegisteredDomainEvent, self._handle_tenant_registered)
        self._bus.subscribe(PlanChangedDomainEvent, self._handle_plan_changed)
        self._bus.subscribe(LeadCreatedDomainEvent, self._handle_lead_created)

    def _handle_tenant_registered(self, e: TenantRegisteredDomainEvent) -> None:
        self._repo.append(_InternalAuditLog(
            audit_id=f"AUD_{uuid.uuid4().hex[:8].upper()}",
            tenant_id=e.tenant_id,
            event_type=e.event_name,
            summary=f"Novo tenant '{e.company_name}' cadastrado com plano '{e.initial_plan}'. Admin: {e.admin_email}",
        ))

    def _handle_plan_changed(self, e: PlanChangedDomainEvent) -> None:
        self._repo.append(_InternalAuditLog(
            audit_id=f"AUD_{uuid.uuid4().hex[:8].upper()}",
            tenant_id=e.tenant_id,
            event_type=e.event_name,
            summary=f"Plano alterado de '{e.old_plan}' para '{e.new_plan}'.",
        ))

    def _handle_lead_created(self, e: LeadCreatedDomainEvent) -> None:
        self._repo.append(_InternalAuditLog(
            audit_id=f"AUD_{uuid.uuid4().hex[:8].upper()}",
            tenant_id=e.tenant_id,
            event_type=e.event_name,
            summary=f"Lead '{e.contact_name}' criado com oportunidade de R$ {e.estimated_value:,.2f}.",
        ))

    def list_logs_for_tenant(self, tenant_id: str) -> List[AuditEntryDto]:
        return [
            AuditEntryDto(
                audit_id=l.audit_id,
                tenant_id=l.tenant_id,
                event_type=l.event_type,
                summary=l.summary,
                timestamp=l.timestamp,
            )
            for l in self._repo.list_by_tenant(tenant_id)
        ]

    def list_all_logs(self) -> List[AuditEntryDto]:
        return [
            AuditEntryDto(
                audit_id=l.audit_id,
                tenant_id=l.tenant_id,
                event_type=l.event_type,
                summary=l.summary,
                timestamp=l.timestamp,
            )
            for l in self._repo.list_all()
        ]
