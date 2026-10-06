"""Contrato Público do Módulo Payroll (Folha de Pagamento e Holerites)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class PayslipDto:
    payslip_id: str
    employee_id: str
    month: str
    base_salary: float
    overtime_pay: float
    absence_deduction: float
    net_salary: float


class IPayrollModule(ABC):
    @abstractmethod
    def get_payslip(self, employee_id: str, month: str) -> Optional[PayslipDto]:
        pass

    @abstractmethod
    def list_month(self, month: str) -> List[PayslipDto]:
        pass
