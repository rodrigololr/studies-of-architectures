"""
in_memory_audit_adapter.py - Adaptador Secundário de Repositório de Auditoria.

Implementa `PaymentAuditRepositoryPort` em memória para persistência auditável.
"""

from __future__ import annotations
from typing import List
from domain.models import PaymentResponse
from ports.driven import PaymentAuditRepositoryPort


class InMemoryPaymentAuditAdapter(PaymentAuditRepositoryPort):
    def __init__(self) -> None:
        self._records: List[PaymentResponse] = []

    def save_audit(self, response: PaymentResponse) -> None:
        self._records.append(response)

    def list_history(self) -> List[PaymentResponse]:
        return list(self._records)
