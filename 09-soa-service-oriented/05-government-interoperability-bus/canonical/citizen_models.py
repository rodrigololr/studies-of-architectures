"""Canonical Data Model (CDM) - Modelo Canônico do Cidadão para Interoperabilidade Governamental."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class FiscalStatus(Enum):
    REGULAR = "REGULAR"
    PENDENTE = "PENDENTE_REGULARIZACAO"
    SUSPENSO = "SUSPENSO"
    CANCELADO = "CANCELADO"


class LicenseStatus(Enum):
    ACTIVE = "ATIVA"
    SUSPENDED = "SUSPENSA"
    REVOKED = "CASSADA"
    EXPIRED = "VENCIDA"


class MaritalStatus(Enum):
    SINGLE = "SOLTEIRO(A)"
    MARRIED = "CASADO(A)"
    DIVORCED = "DIVORCIADO(A)"
    WIDOWED = "VIUVO(A)"


@dataclass(frozen=True)
class TaxIdentificationRecord:
    cpf: str
    full_name: str
    birth_date: str
    fiscal_status: FiscalStatus


@dataclass(frozen=True)
class DriverLicenseRecord:
    cnh_number: str
    category: str
    points: int
    license_status: LicenseStatus
    valid_until: str


@dataclass(frozen=True)
class CivilRegistryRecord:
    certidao_matricula: str
    marital_status: MaritalStatus
    cartorio_municipio: str


@dataclass(frozen=True)
class UnifiedCitizenRecord:
    cpf: str
    tax_info: TaxIdentificationRecord
    driver_info: Optional[DriverLicenseRecord] = None
    civil_info: Optional[CivilRegistryRecord] = None
    access_restrictions_applied: Optional[List[str]] = None
