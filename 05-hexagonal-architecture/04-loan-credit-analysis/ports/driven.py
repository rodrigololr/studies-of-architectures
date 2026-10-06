"""
driven.py - Portas Secundárias / Outbound da esteira de crédito.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models import BureauScore, RiskRating, CreditAnalysisResult


class CreditBureauPort(ABC):
    @property
    @abstractmethod
    def bureau_name(self) -> str:
        """Identificador do birô de proteção ao crédito."""
        pass

    @abstractmethod
    def query_score(self, cpf: str) -> Optional[BureauScore]:
        """Consulta o score e apontamentos de dívidas ativas."""
        pass


class CentralBankScrPort(ABC):
    @abstractmethod
    def get_total_financial_commitments(self, cpf: str) -> float:
        """Consulta o valor total de dívidas já contratadas em outros bancos no SCR."""
        pass


class InterestRatePolicyPort(ABC):
    @abstractmethod
    def get_annual_rate(self, risk_rating: RiskRating) -> float:
        """Determina a taxa de juros anual com base na classificação de risco calculada."""
        pass


class CreditDossierRepositoryPort(ABC):
    @abstractmethod
    def save(self, result: CreditAnalysisResult) -> None:
        """Persiste o laudo de análise de crédito."""
        pass

    @abstractmethod
    def find_by_proposal_id(self, proposal_id: str) -> Optional[CreditAnalysisResult]:
        """Busca o laudo de crédito pelo ID da proposta."""
        pass
