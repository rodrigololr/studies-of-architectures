"""
protocol.py - Protocolo binário/JSON de comunicação com o Servidor de Banco de Dados.

Suporta comandos de PING (Heartbeat), EXECUTE (consultas) e CLOSE.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import json
from typing import Any, List, Optional


class DbAction(str, Enum):
    PING = "PING"
    EXECUTE = "EXECUTE"
    CLOSE = "CLOSE"


@dataclass(frozen=True)
class DbCommand:
    command_id: str
    action: DbAction
    query_text: str = ""

    def serialize(self) -> bytes:
        payload = {
            "id": self.command_id,
            "action": self.action.value,
            "query": self.query_text,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[DbCommand]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                command_id=data["id"],
                action=DbAction(data["action"]),
                query_text=data.get("query", ""),
            )
        except Exception:
            return None


@dataclass(frozen=True)
class DbResult:
    command_id: str
    success: bool
    data: List[Any]
    error: Optional[str] = None

    def serialize(self) -> bytes:
        payload = {
            "id": self.command_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[DbResult]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                command_id=data["id"],
                success=bool(data["success"]),
                data=data.get("data", []),
                error=data.get("error"),
            )
        except Exception:
            return None
