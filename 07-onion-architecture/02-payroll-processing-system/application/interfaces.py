"""
application/interfaces.py - Camada 3: Application Interfaces.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.model.employee import Employee
from domain.model.payslip import Payslip


class IEmployeeRepository(ABC):
    @abstractmethod
    def list_active_employees(self) -> List[Employee]:
        pass

    @abstractmethod
    def find_by_id(self, employee_id: str) -> Optional[Employee]:
        pass


class IPayrollSlipRepository(ABC):
    @abstractmethod
    def save(self, payslip: Payslip) -> None:
        pass

    @abstractmethod
    def list_by_period(self, reference_period: str) -> List[Payslip]:
        pass


class IBankPayrollTransferGateway(ABC):
    @abstractmethod
    def dispatch_direct_deposits(self, deposits: List[tuple[str, str, float]]) -> bool:
        """Envia lote de créditos em conta corrente (employee_id, employee_name, net_amount)."""
        pass
