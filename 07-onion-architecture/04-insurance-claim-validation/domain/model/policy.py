"""Entidade de Apólice de Seguro (Insurance Policy)."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from .exceptions import PolicyExpiredException, PolicySuspendedException


class PolicyStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class CoverageType(Enum):
    AUTO = "AUTO"
    HOME = "HOME"
    LIFE = "LIFE"
    HEALTH = "HEALTH"


@dataclass
class Policy:
    """Entidade do Domínio: Apólice de Seguro contratada."""
    policy_id: str
    policy_number: str
    insured_name: str
    coverage_type: CoverageType
    start_date: datetime
    end_date: datetime
    coverage_limit: float  # Limite Máximo de Indenização (LMI)
    deductible: float  # Franquia obrigatória
    status: PolicyStatus = PolicyStatus.ACTIVE
    excluded_causes: List[str] = field(default_factory=lambda: ["GUERRA", "ATENTADO_TERRORISTA", "DESGASTE_NATURAL"])

    def validate_eligibility_for_event(self, occurrence_date: datetime) -> None:
        """Garante as invariantes contratuais no momento da ocorrência do sinistro."""
        if self.status == PolicyStatus.SUSPENDED:
            raise PolicySuspendedException(f"Apólice {self.policy_number} está suspensa por inadimplência.")
        if self.status in (PolicyStatus.EXPIRED, PolicyStatus.CANCELLED):
            raise PolicyExpiredException(f"Apólice {self.policy_number} está inativa ({self.status.value}).")

        if occurrence_date < self.start_date or occurrence_date > self.end_date:
            raise PolicyExpiredException(
                f"Data do sinistro ({occurrence_date.strftime('%d/%m/%Y')}) fora do período de vigência "
                f"({self.start_date.strftime('%d/%m/%Y')} até {self.end_date.strftime('%d/%m/%Y')})."
            )

    def is_cause_excluded(self, cause: str) -> bool:
        """Checa se a causa informada é expressamente excluída da cobertura."""
        return cause.upper() in [ex.upper() for ex in self.excluded_causes]
