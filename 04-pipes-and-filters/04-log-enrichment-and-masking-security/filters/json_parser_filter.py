"""
json_parser_filter.py - Filtro 1: Parser de JSON de Log.

Desserializa a linha de log JSON em um objeto LogEvent estruturado.
"""

from __future__ import annotations
import json
from typing import Optional
from pipeline.base import Filter
from pipeline.context import LogEvent


class JsonLogParserFilter(Filter[str, LogEvent]):
    def process(self, raw_line: str) -> Optional[LogEvent]:
        line = raw_line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
            return LogEvent(
                raw_text=raw_line,
                timestamp=data.get("timestamp", ""),
                level=data.get("level", "INFO").upper(),
                service_name=data.get("service", "unknown-service"),
                client_ip=data.get("client_ip", "127.0.0.1"),
                message=data.get("message", ""),
            )
        except json.JSONDecodeError as ex:
            return LogEvent(
                raw_text=raw_line,
                is_valid=False,
                error_message=f"Linha de log JSON inválida: {ex}",
            )
