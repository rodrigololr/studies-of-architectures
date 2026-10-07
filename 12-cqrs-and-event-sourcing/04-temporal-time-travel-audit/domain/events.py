from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    version: int
    timestamp: datetime
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class EmployeeHired(DomainEvent):
    full_name: str = ""
    role: str = ""
    department: str = ""
    salary: float = 0.0

@dataclass(frozen=True)
class DepartmentTransferred(DomainEvent):
    previous_department: str = ""
    new_department: str = ""
    reason: str = ""

@dataclass(frozen=True)
class SalaryAdjusted(DomainEvent):
    previous_salary: float = 0.0
    new_salary: float = 0.0
    justification: str = ""

@dataclass(frozen=True)
class RolePromoted(DomainEvent):
    previous_role: str = ""
    new_role: str = ""
    rank_level: int = 1

@dataclass(frozen=True)
class BonusAwarded(DomainEvent):
    amount: float = 0.0
    reason: str = ""
