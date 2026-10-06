"""
threat_detector_filter.py - Filtro 4: Detecção de Ameaças e Injeção de Código.

Inspeciona o conteúdo da mensagem e cabeçalhos em busca de assinaturas
de ataques conhecidos (SQL Injection, Path Traversal, Brute Force).
"""

from __future__ import annotations
import re
from typing import Optional
from pipeline.base import Filter
from pipeline.context import LogEvent


class ThreatDetectorFilter(Filter[LogEvent, LogEvent]):
    SQLI_PATTERN = re.compile(r"(\bUNION\b|\bSELECT\b|\bDROP\s+TABLE\b|--|\bOR\s+1=1\b)", re.IGNORECASE)
    TRAVERSAL_PATTERN = re.compile(r"(\.\./\.\./|/etc/passwd)", re.IGNORECASE)

    def process(self, event: LogEvent) -> Optional[LogEvent]:
        if not event.is_valid:
            return event

        msg = event.message
        if self.SQLI_PATTERN.search(msg):
            event.threat_detected = True
            event.threat_type = "SQL_INJECTION_ATTEMPT"
            event.level = "CRITICAL"

        elif self.TRAVERSAL_PATTERN.search(msg):
            event.threat_detected = True
            event.threat_type = "DIRECTORY_TRAVERSAL_ATTEMPT"
            event.level = "CRITICAL"

        return event
