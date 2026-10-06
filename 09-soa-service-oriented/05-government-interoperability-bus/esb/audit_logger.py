"""Trilha de Auditoria Corporativa e Conformidade LGPD."""

import datetime
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AuditLogEntry:
    timestamp: str
    consumer_id: str
    cpf_consultado: str
    services_accessed: List[str]
    access_granted: bool
    details: str


class AuditLogger:
    """Registrador de auditoria imutável do ESB."""

    def __init__(self) -> None:
        self._entries: List[AuditLogEntry] = []

    def record_access(
        self,
        consumer_id: str,
        cpf: str,
        services: List[str],
        granted: bool,
        details: str,
    ) -> None:
        entry = AuditLogEntry(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            consumer_id=consumer_id,
            cpf_consultado=cpf,
            services_accessed=services,
            access_granted=granted,
            details=details,
        )
        self._entries.append(entry)

    @property
    def entries(self) -> List[AuditLogEntry]:
        return list(self._entries)
