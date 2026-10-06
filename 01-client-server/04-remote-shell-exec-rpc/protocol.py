"""
protocol.py - Contrato e Protocolo para o Mini RPC (JSON-RPC sobre TCP).

Padroniza chamadas de procedimentos remotos com enquadramento por linha (\\n),
suporte a autenticação por token, parâmetros nomeados e respostas estruturadas.
"""

from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class RpcRequest:
    request_id: str
    auth_token: str
    method: str
    params: Dict[str, Any]

    def serialize(self) -> bytes:
        payload = {
            "id": self.request_id,
            "token": self.auth_token,
            "method": self.method,
            "params": self.params,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[RpcRequest]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                request_id=data["id"],
                auth_token=data["token"],
                method=data["method"],
                params=data.get("params", {}),
            )
        except Exception:
            return None


@dataclass(frozen=True)
class RpcResponse:
    request_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def serialize(self) -> bytes:
        payload = {
            "id": self.request_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[RpcResponse]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                request_id=data["id"],
                success=bool(data["success"]),
                result=data.get("result"),
                error=data.get("error"),
                execution_time_ms=float(data.get("execution_time_ms", 0.0)),
            )
        except Exception:
            return None
