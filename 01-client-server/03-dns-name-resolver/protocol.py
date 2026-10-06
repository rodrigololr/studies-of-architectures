"""
protocol.py - Protocolo de Mensagens de Resolução de Nomes (Mini-DNS UDP).

Trabalha sobre datagramas UDP: pacotes individuais sem conexão prévia,
contendo pergunta (Query) ou resposta autoritativa (Response).
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import json
from typing import Optional


class QueryType(str, Enum):
    A = "A"        # IPv4
    CNAME = "CNAME"


@dataclass(frozen=True)
class DnsQuery:
    query_id: int
    domain: str
    record_type: QueryType

    def serialize(self) -> bytes:
        data = {
            "id": self.query_id,
            "type": "QUERY",
            "domain": self.domain.lower().strip(),
            "record_type": self.record_type.value,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, raw_bytes: bytes) -> Optional[DnsQuery]:
        try:
            data = json.loads(raw_bytes.decode("utf-8"))
            if data.get("type") != "QUERY":
                return None
            return cls(
                query_id=int(data["id"]),
                domain=data["domain"],
                record_type=QueryType(data["record_type"]),
            )
        except Exception:
            return None


@dataclass(frozen=True)
class DnsResponse:
    query_id: int
    domain: str
    record_type: QueryType
    resolved_ip: Optional[str]
    ttl_seconds: int
    found: bool

    def serialize(self) -> bytes:
        data = {
            "id": self.query_id,
            "type": "RESPONSE",
            "domain": self.domain,
            "record_type": self.record_type.value,
            "ip": self.resolved_ip,
            "ttl": self.ttl_seconds,
            "found": self.found,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, raw_bytes: bytes) -> Optional[DnsResponse]:
        try:
            data = json.loads(raw_bytes.decode("utf-8"))
            if data.get("type") != "RESPONSE":
                return None
            return cls(
                query_id=int(data["id"]),
                domain=data["domain"],
                record_type=QueryType(data["record_type"]),
                resolved_ip=data.get("ip"),
                ttl_seconds=int(data.get("ttl", 0)),
                found=bool(data.get("found", False)),
            )
        except Exception:
            return None
