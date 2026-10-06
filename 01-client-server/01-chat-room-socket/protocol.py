"""
protocol.py - Definição do protocolo de comunicação do Chat Room.

Utiliza delimitador de nova linha (\\n) para garantir o enquadramento de mensagens
sobre o fluxo contínuo de bytes do TCP (evitando problemas de fragmentação de pacotes).
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
import json
from typing import Optional


class MessageType(str, Enum):
    JOIN = "JOIN"
    CHAT = "CHAT"
    LEAVE = "LEAVE"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True)
class Message:
    message_type: MessageType
    sender: str
    content: str
    timestamp: Optional[str] = None

    def serialize(self) -> bytes:
        """Serializa o objeto para bytes com delimitador de linha."""
        payload = {
            "type": self.message_type.value,
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[Message]:
        """Desserializa uma linha JSON para o objeto Message."""
        try:
            data = json.loads(raw_line.strip())
            return cls(
                message_type=MessageType(data["type"]),
                sender=data["sender"],
                content=data["content"],
                timestamp=data.get("timestamp"),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
