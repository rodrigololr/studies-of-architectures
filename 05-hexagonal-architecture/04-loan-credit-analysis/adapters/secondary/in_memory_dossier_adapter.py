"""
in_memory_dossier_adapter.py - Adaptador Secundário de Repositório de Laudos de Crédito.
"""

from __future__ import annotations
from typing import Dict, Optional
from domain.models import CreditAnalysisResult
from ports.driven import CreditDossierRepositoryPort


class InMemoryCreditDossierAdapter(CreditDossierRepositoryPort):
    def __init__(self) -> None:
        self._dossiers: Dict[str, CreditAnalysisResult] = {}

    def save(self, result: CreditAnalysisResult) -> None:
        self._dossiers[result.proposal_id] = result

    def find_by_proposal_id(self, proposal_id: str) -> Optional[CreditAnalysisResult]:
        return self._dossiers.get(proposal_id)
