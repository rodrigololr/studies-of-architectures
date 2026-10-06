"""Implementação Interna Privada do Módulo Payments."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalPaymentTransaction:
    transaction_id: str
    order_id: str
    customer_email: str
    amount: float
    payment_method: str
    status: str  # "APPROVED", "DECLINED"
    auth_code: Optional[str]
    created_at: datetime


class _InternalPaymentRepository:
    """Repositório privado com persistência em memória do schema 'payments'."""
    def __init__(self) -> None:
        self._txs: Dict[str, _InternalPaymentTransaction] = {}

    def save(self, tx: _InternalPaymentTransaction) -> None:
        self._txs[tx.transaction_id] = tx

    def find_by_id(self, tx_id: str) -> Optional[_InternalPaymentTransaction]:
        return self._txs.get(tx_id)

    def find_by_order_id(self, order_id: str) -> Optional[_InternalPaymentTransaction]:
        for tx in self._txs.values():
            if tx.order_id == order_id:
                return tx
        return None
