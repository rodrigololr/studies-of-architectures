"""Canonical Data Model (CDM) - Modelo Canônico de Provisionamento de Telecom."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SubscriberInfo:
    name: str
    cpf: str
    email: str


@dataclass(frozen=True)
class LineDetails:
    msisdn: str      # Número de telefone (ex: "+5511988887777")
    iccid_sim: str   # Identificador do chip SIM físico (19 dígitos)
    plan_code: str   # ex: "POS_ILIMITADO_50GB"
    monthly_fee: float


@dataclass(frozen=True)
class CanonicalProvisioningRequest:
    order_id: str
    subscriber: SubscriberInfo
    line: LineDetails


@dataclass(frozen=True)
class CanonicalProvisioningResponse:
    order_id: str
    msisdn: str
    status: str  # "ACTIVATED", "COMPENSATED_FAILED", "REJECTED_INVENTORY"
    hlr_routing_code: Optional[str]
    billing_cycle_day: Optional[int]
    message: str
