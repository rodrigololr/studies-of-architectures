"""
bacen_scr_adapter.py - Adaptador Secundário para consulta ao Sistema de Informações de Crédito (SCR) do Banco Central.
"""

from __future__ import annotations
from typing import Dict
from ports.driven import CentralBankScrPort


class BacenScrAdapter(CentralBankScrPort):
    def __init__(self, commitments_db: Dict[str, float]) -> None:
        # Mapeia CPF -> Total de dívidas ativas contratadas no Sistema Financeiro Nacional
        self._commitments = commitments_db

    def get_total_financial_commitments(self, cpf: str) -> float:
        return self._commitments.get(cpf, 0.0)
