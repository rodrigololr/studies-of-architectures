"""Contrato Público do Módulo Employees (Cadastro e Quadro de Pessoal)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class EmployeeDto:
    employee_id: str
    name: str
    cpf: str
    role: str
    department: str
    base_salary: float
    is_active: bool


@dataclass(frozen=True)
class RegisterEmployeeCommand:
    name: str
    cpf: str
    role: str
    department: str
    base_salary: float


class IEmployeeModule(ABC):
    @abstractmethod
    def register_employee(self, cmd: RegisterEmployeeCommand) -> EmployeeDto:
        pass

    @abstractmethod
    def get_employee(self, employee_id: str) -> Optional[EmployeeDto]:
        pass

    @abstractmethod
    def list_active(self) -> List[EmployeeDto]:
        pass
