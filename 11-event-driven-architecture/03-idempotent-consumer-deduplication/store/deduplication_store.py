"""Deduplication Store / Ledger de Idempotência Atômico (Redis / DB Simulator)."""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class IdempotencyRecord:
    key: str
    status: str  # "PROCESSING", "PROCESSED"
    result: Dict[str, Any] = field(default_factory=dict)
    first_seen_timestamp: float = field(default_factory=time.time)
    execution_count: int = 1


class IdempotencyStore:
    """Repositório de chaves de idempotência para desduplicação atômica."""

    def __init__(self) -> None:
        self._records: Dict[str, IdempotencyRecord] = {}

    def try_claim_key(self, key: str) -> bool:
        """Tenta reservar a chave de forma atômica (simulando SETNX no Redis).
        
        Retorna True se for a PRIMEIRA vez que a mensagem é vista.
        Retorna False se a mensagem for uma DUPLICATA.
        """
        if key in self._records:
            self._records[key].execution_count += 1
            return False

        self._records[key] = IdempotencyRecord(key=key, status="PROCESSING")
        return True

    def mark_processed(self, key: str, result_data: Dict[str, Any]) -> None:
        if key in self._records:
            self._records[key].status = "PROCESSED"
            self._records[key].result = result_data

    def get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        record = self._records.get(key)
        return record.result if record and record.status == "PROCESSED" else None

    def get_execution_count(self, key: str) -> int:
        record = self._records.get(key)
        return record.execution_count if record else 0
