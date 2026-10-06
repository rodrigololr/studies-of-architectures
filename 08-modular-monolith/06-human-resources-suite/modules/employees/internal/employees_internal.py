"""Implementação Interna do Módulo Employees (Schema: employees)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class _InternalEmployee:
    employee_id: str
    name: str
    cpf: str
    role: str
    department: str
    base_salary: float
    is_active: bool = True
    hired_at: datetime = field(default_factory=datetime.now)


class _InternalEmployeeRepository:
    def __init__(self) -> None:
        self._employees: Dict[str, _InternalEmployee] = {}

    def save(self, emp: _InternalEmployee) -> None:
        self._employees[emp.employee_id] = emp

    def find_by_id(self, emp_id: str) -> Optional[_InternalEmployee]:
        return self._employees.get(emp_id)

    def list_all(self) -> List[_InternalEmployee]:
        return list(self._employees.values())
