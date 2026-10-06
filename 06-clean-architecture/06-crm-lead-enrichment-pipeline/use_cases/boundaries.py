"""
use_cases/boundaries.py - Camada 2: Boundaries e Gateways de CRM.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from entities.models import Lead, SalesRep, RepTier
from use_cases.dto import IngestLeadRequestModel, IngestLeadResponseModel


class IngestLeadInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: IngestLeadRequestModel) -> None:
        pass


class IngestLeadOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: IngestLeadResponseModel) -> None:
        pass


class LeadRepositoryGateway(ABC):
    @abstractmethod
    def save(self, lead: Lead) -> None:
        pass

    @abstractmethod
    def find_by_id(self, lead_id: str) -> Optional[Lead]:
        pass


class FirmographicEnrichmentGateway(ABC):
    @abstractmethod
    def lookup_company(self, domain_or_name: str) -> Tuple[int, float]:
        """Consulta provedores de inteligência de mercado (funcionários, faturamento)."""
        pass


class SalesRepRepositoryGateway(ABC):
    @abstractmethod
    def find_available_by_tier(self, tier: RepTier) -> Optional[SalesRep]:
        pass
