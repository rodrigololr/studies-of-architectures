"""Implementação Interna do Módulo Identity (Schema: identity)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalTenant:
    tenant_id: str
    company_name: str
    admin_email: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class _InternalIdentityRepository:
    def __init__(self) -> None:
        self._tenants: Dict[str, _InternalTenant] = {}

    def save(self, tenant: _InternalTenant) -> None:
        self._tenants[tenant.tenant_id] = tenant

    def find_by_id(self, tenant_id: str) -> Optional[_InternalTenant]:
        return self._tenants.get(tenant_id)
