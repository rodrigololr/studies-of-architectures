"""
driver.py - Portas Primárias / Inbound da esteira de crédito.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from domain.models import LoanProposal, CreditAnalysisResult


class UnderwriteCreditProposalUseCasePort(ABC):
    @abstractmethod
    def evaluate(self, proposal: LoanProposal) -> CreditAnalysisResult:
        """Avalia e emite o parecer de crédito da proposta do proponente."""
        pass


class GetCreditDossierUseCasePort(ABC):
    @abstractmethod
    def get_dossier(self, proposal_id: str) -> Optional[CreditAnalysisResult]:
        """Consulta o laudo emitido anteriormente."""
        pass
