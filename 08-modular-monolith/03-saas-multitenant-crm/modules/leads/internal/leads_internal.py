"""Implementação Interna do Módulo Leads (Schema: leads)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class _InternalLead:
    lead_id: str
    tenant_id: str
    contact_name: str
    contact_email: str
    estimated_value: float
    status: str = "NEW"
    created_at: datetime = field(default_factory=datetime.now)


class _InternalLeadRepository:
    def __init__(self) -> None:
        self._leads: Dict[str, _InternalLead] = {}

    def save(self, lead: _InternalLead) -> None:
        self._leads[lead.lead_id] = lead

    def list_by_tenant(self, tenant_id: str) -> List[_InternalLead]:
        return [l for l in self._leads.values() if l.tenant_id == tenant_id]

    def count_by_tenant(self, tenant_id: str) -> int:
        return sum(1 for l in self._leads.values() if l.tenant_id == tenant_id)
