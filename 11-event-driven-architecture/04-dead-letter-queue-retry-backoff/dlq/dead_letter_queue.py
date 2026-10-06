"""Dead-Letter Queue (DLQ) para isolamento de mensagens venenosas (Poison Pills)."""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class DeadLetterMessage:
    message_id: str
    original_topic: str
    payload: Dict[str, Any]
    error_reason: str
    total_retries_attempted: int
    routed_at: float = field(default_factory=time.time)


class DeadLetterQueue:
    """Fila de Mensagens Mortas (DLQ) para inspeção, auditoria e reprocessamento."""

    def __init__(self) -> None:
        self._dead_messages: Dict[str, DeadLetterMessage] = {}

    def enqueue_poison_pill(self, dl_msg: DeadLetterMessage) -> None:
        self._dead_messages[dl_msg.message_id] = dl_msg

    def get_message(self, message_id: str) -> Optional[DeadLetterMessage]:
        return self._dead_messages.get(message_id)

    @property
    def all_messages(self) -> List[DeadLetterMessage]:
        return list(self._dead_messages.values())

    def remove_for_replay(self, message_id: str) -> Optional[DeadLetterMessage]:
        return self._dead_messages.pop(message_id, None)
