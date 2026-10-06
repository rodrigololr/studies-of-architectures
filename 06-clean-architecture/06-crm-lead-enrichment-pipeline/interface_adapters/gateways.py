"""
interface_adapters/gateways.py - Camada 3: Gateways e Repositórios de CRM.
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple
from entities.models import Lead, SalesRep, RepTier
from use_cases.boundaries import (
    LeadRepositoryGateway,
    FirmographicEnrichmentGateway,
    SalesRepRepositoryGateway,
)


class InMemoryLeadRepository(LeadRepositoryGateway):
    def __init__(self) -> None:
        self._leads: Dict[str, Lead] = {}

    def save(self, lead: Lead) -> None:
        self._leads[lead.lead_id] = lead

    def find_by_id(self, lead_id: str) -> Optional[Lead]:
        return self._leads.get(lead_id)


class MockFirmographicGateway(FirmographicEnrichmentGateway):
    def __init__(self) -> None:
        # Mock de dados firmográficos (Clearbit / ZoomInfo)
        # Empresa -> (funcionarios, faturamento_anual)
        self._db: Dict[str, Tuple[int, float]] = {
            "nubank": (8000, 1_500_000_000.0),
            "techcorp sa": (1200, 85_000_000.0),
            "varejo digital": (250, 4_500_000.0),
            "padaria do bairro": (8, 120_000.0),
        }

    def lookup_company(self, domain_or_name: str) -> Tuple[int, float]:
        key = domain_or_name.lower().strip()
        for known_name, data in self._db.items():
            if known_name in key:
                return data
        # Default para empresas não catalogadas
        return 15, 300_000.0


class InMemorySalesRepRepository(SalesRepRepositoryGateway):
    def __init__(self, reps: Optional[Dict[str, SalesRep]] = None) -> None:
        self._reps: Dict[str, SalesRep] = dict(reps or {})

    def find_available_by_tier(self, tier: RepTier) -> Optional[SalesRep]:
        for rep in self._reps.values():
            if rep.tier == tier and rep.is_active:
                return rep
        return None
