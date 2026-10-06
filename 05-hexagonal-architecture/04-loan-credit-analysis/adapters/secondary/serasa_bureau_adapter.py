"""
serasa_bureau_adapter.py - Adaptador Secundário para Serasa Experian.
"""

from __future__ import annotations
from typing import Dict, Optional
from domain.models import BureauScore
from ports.driven import CreditBureauPort


class SerasaBureauAdapter(CreditBureauPort):
    def __init__(self, database_records: Dict[str, tuple[int, bool]]) -> None:
        # Formato do mock: CPF -> (score, tem_negativacao)
        self._records = database_records

    @property
    def bureau_name(self) -> str:
        return "Serasa Experian"

    def query_score(self, cpf: str) -> Optional[BureauScore]:
        data = self._records.get(cpf, (600, False))
        return BureauScore(
            bureau_name=self.bureau_name,
            score=data[0],
            has_active_defaults=data[1],
        )
