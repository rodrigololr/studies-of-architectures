"""Implementação Interna do Módulo Payroll (Schema: payroll)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class _InternalPayslip:
    payslip_id: str
    employee_id: str
    month: str
    base_salary: float
    overtime_pay: float
    absence_deduction: float
    net_salary: float
    calculated_at: datetime = field(default_factory=datetime.now)


class _InternalPayrollRepository:
    def __init__(self) -> None:
        self._payslips: Dict[str, _InternalPayslip] = {}

    def save(self, ps: _InternalPayslip) -> None:
        key = f"{ps.employee_id}_{ps.month}"
        self._payslips[key] = ps

    def find(self, employee_id: str, month: str) -> Optional[_InternalPayslip]:
        key = f"{employee_id}_{month}"
        return self._payslips.get(key)

    def list_by_month(self, month: str) -> List[_InternalPayslip]:
        return [p for p in self._payslips.values() if p.month == month]
