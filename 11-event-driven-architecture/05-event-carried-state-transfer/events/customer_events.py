"""Event-Carried State Transfer (ECST) Event Models."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class AddressSnapshot:
    street: str
    number: str
    city: str
    state: str
    postal_code: str


@dataclass(frozen=True)
class CustomerSnapshot:
    """Snapshot completo e denormalizado do estado da entidade."""
    customer_id: str
    full_name: str
    tax_id: str             # CPF / CNPJ
    email: str
    tier: str               # "STANDARD", "GOLD", "PLATINUM"
    billing_address: AddressSnapshot


@dataclass(frozen=True)
class CustomerProfileUpdatedEvent:
    """Evento que carrega o estado completo (ECST)."""
    event_id: str
    sequence_number: int
    customer: CustomerSnapshot
    occurred_at: float = field(default_factory=time.time)
