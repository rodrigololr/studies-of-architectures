"""Implementação Interna do Módulo Audit (Schema: audit)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class _InternalAuditLog:
    audit_id: str
    tenant_id: str
    event_type: str
    summary: str
    timestamp: datetime = field(default_factory=datetime.now)


class _InternalAuditRepository:
    def __init__(self) -> None:
        self._logs: List[_InternalAuditLog] = []

    def append(self, log: _InternalAuditLog) -> None:
        self._logs.append(log)

    def list_by_tenant(self, tenant_id: str) -> List[_InternalAuditLog]:
        return [l for l in self._logs if l.tenant_id == tenant_id]

    def list_all(self) -> List[_InternalAuditLog]:
        return list(self._logs)
