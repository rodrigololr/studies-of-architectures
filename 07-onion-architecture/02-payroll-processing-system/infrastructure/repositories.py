"""
infrastructure/repositories.py - Camada 4: Infrastructure (Casca Externa).
"""

from __future__ import annotations
from typing import Dict, List, Optional
from domain.model.employee import Employee
from domain.model.payslip import Payslip
from application.interfaces import IEmployeeRepository, IPayrollSlipRepository


class InMemoryEmployeeRepository(IEmployeeRepository):
    def __init__(self, employees: Optional[Dict[str, Employee]] = None) -> None:
        self._employees: Dict[str, Employee] = dict(employees or {})

    def list_active_employees(self) -> List[Employee]:
        return [e for e in self._employees.values() if e.is_active]

    def find_by_id(self, employee_id: str) -> Optional[Employee]:
        return self._employees.get(employee_id)


class InMemoryPayrollSlipRepository(IPayrollSlipRepository):
    def __init__(self) -> None:
        self._slips: Dict[str, Payslip] = {}

    def save(self, payslip: Payslip) -> None:
        self._slips[payslip.payslip_id] = payslip

    def list_by_period(self, reference_period: str) -> List[Payslip]:
        return [s for s in self._slips.values() if s.reference_period == reference_period]
