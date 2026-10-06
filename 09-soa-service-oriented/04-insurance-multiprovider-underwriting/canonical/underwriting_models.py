"""Canonical Data Model (CDM) - Modelo Canônico de Subscrição de Seguros (Underwriting)."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CoverageType(Enum):
    BASIC = "BASIC"          # Roubo e Furto apenas
    STANDARD = "STANDARD"    # Colisão, Roubo e Furto
    COMPREHENSIVE = "COMPREHENSIVE"  # Compreensiva (Colisão, Danos Terceiros, Assistência 24h)


@dataclass(frozen=True)
class VehicleInfo:
    make: str             # ex: "Toyota"
    model: str            # ex: "Corolla XEi"
    year: int             # ex: 2022
    fipe_value_brl: float # ex: 120000.0


@dataclass(frozen=True)
class DriverProfile:
    age: int              # ex: 35
    gender: str           # "M", "F", "NB"
    license_years: int    # Tempo de CNH
    has_garage: bool      # Possui garagem fechada


@dataclass(frozen=True)
class CanonicalQuoteRequest:
    request_id: str
    vehicle: VehicleInfo
    driver: DriverProfile
    coverage: CoverageType


@dataclass(frozen=True)
class QuoteProposal:
    carrier_name: str
    carrier_protocol: str
    annual_premium_brl: float
    deductible_brl: float
    coverage: CoverageType
    is_eligible: bool
    rejection_reason: Optional[str] = None


@dataclass(frozen=True)
class AggregatedQuoteResult:
    request_id: str
    total_requested: int
    successful_proposals: List[QuoteProposal]
    failed_carriers: List[str]
    best_value_carrier: Optional[str] = None
    cheapest_premium_brl: Optional[float] = None
