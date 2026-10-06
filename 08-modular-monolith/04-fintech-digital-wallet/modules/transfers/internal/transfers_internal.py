"""Implementação Interna do Módulo Transfers (Schema: transfers)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalTransfer:
    transfer_id: str
    origin_account_id: str
    destination_pix_key: str
    amount: float
    status: str
    authorization_code: Optional[str]
    created_at: datetime = field(default_factory=datetime.now)


class _InternalTransfersRepository:
    def __init__(self) -> None:
        self._transfers: Dict[str, _InternalTransfer] = {}

    def save(self, tx: _InternalTransfer) -> None:
        self._transfers[tx.transfer_id] = tx

    def find_by_id(self, tx_id: str) -> Optional[_InternalTransfer]:
        return self._transfers.get(tx_id)
