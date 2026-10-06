"""Contrato Público do Módulo Identity."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class TenantDto:
    tenant_id: str
    company_name: str
    admin_email: str
    is_active: bool


@dataclass(frozen=True)
class RegisterTenantCommand:
    company_name: str
    admin_email: str
    initial_plan: str  # "STARTER", "PRO", "ENTERPRISE"


@dataclass(frozen=True)
class TenantRegisteredDomainEvent(DomainEvent):
    company_name: str = ""
    admin_email: str = ""
    initial_plan: str = ""


class IIdentityModule(ABC):
    @abstractmethod
    def register_tenant(self, cmd: RegisterTenantCommand) -> TenantDto:
        pass

    @abstractmethod
    def get_tenant(self, tenant_id: str) -> Optional[TenantDto]:
        pass
