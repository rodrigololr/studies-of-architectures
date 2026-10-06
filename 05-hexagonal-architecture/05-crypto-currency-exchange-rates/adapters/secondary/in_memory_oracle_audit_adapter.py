"""
in_memory_oracle_audit_adapter.py - Adaptador Secundário de Repositório de Auditoria do Oráculo.
"""

from __future__ import annotations
from typing import List
from domain.models import AggregatedRate
from ports.driven import PriceOracleAuditRepositoryPort


class InMemoryOracleAuditAdapter(PriceOracleAuditRepositoryPort):
    def __init__(self) -> None:
        self._rates: List[AggregatedRate] = []

    def record_rate(self, rate: AggregatedRate) -> None:
        self._rates.append(rate)

    def list_history(self) -> List[AggregatedRate]:
        return list(self._rates)
