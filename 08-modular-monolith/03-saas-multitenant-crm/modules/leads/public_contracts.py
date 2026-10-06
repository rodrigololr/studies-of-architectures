"""Contrato Público do Módulo Leads."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from shared.events import DomainEvent


class QuotaExceededError(Exception):
    """Lançada quando a cota de leads do plano contratado é atingida."""
    pass


@dataclass(frozen=True)
class CreateLeadCommand:
    tenant_id: str
    contact_name: str
    contact_email: str
    estimated_value: float


@dataclass(frozen=True)
class LeadDto:
    lead_id: str
    tenant_id: str
    contact_name: str
    contact_email: str
    estimated_value: float
    status: str  # "NEW", "CONTACTED", "QUALIFIED", "WON", "LOST"


@dataclass(frozen=True)
class LeadCreatedDomainEvent(DomainEvent):
    lead_id: str = ""
    contact_name: str = ""
    estimated_value: float = 0.0


class ILeadsModule(ABC):
    @abstractmethod
    def create_lead(self, cmd: CreateLeadCommand) -> LeadDto:
        pass

    @abstractmethod
    def list_leads(self, tenant_id: str) -> List[LeadDto]:
        pass

    @abstractmethod
    def count_leads(self, tenant_id: str) -> int:
        pass
