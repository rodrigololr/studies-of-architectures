"""Contrato Público do Módulo Audit."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class AuditEntryDto:
    audit_id: str
    tenant_id: str
    event_type: str
    summary: str
    timestamp: datetime


class IAuditModule(ABC):
    @abstractmethod
    def list_logs_for_tenant(self, tenant_id: str) -> List[AuditEntryDto]:
        pass

    @abstractmethod
    def list_all_logs(self) -> List[AuditEntryDto]:
        pass
