"""Ponto de Entrada e Facade do Módulo Employees."""

import uuid
from typing import Optional, List
from modules.employees.public_contracts import (
    IEmployeeModule,
    EmployeeDto,
    RegisterEmployeeCommand,
)
from modules.employees.internal.employees_internal import (
    _InternalEmployee,
    _InternalEmployeeRepository,
)


class EmployeesModule(IEmployeeModule):
    def __init__(self) -> None:
        self._repo = _InternalEmployeeRepository()

    def register_employee(self, cmd: RegisterEmployeeCommand) -> EmployeeDto:
        emp_id = f"EMP_{uuid.uuid4().hex[:8].upper()}"
        emp = _InternalEmployee(
            employee_id=emp_id,
            name=cmd.name,
            cpf=cmd.cpf,
            role=cmd.role,
            department=cmd.department,
            base_salary=round(cmd.base_salary, 2),
        )
        self._repo.save(emp)
        return EmployeeDto(
            employee_id=emp.employee_id,
            name=emp.name,
            cpf=emp.cpf,
            role=emp.role,
            department=emp.department,
            base_salary=emp.base_salary,
            is_active=emp.is_active,
        )

    def get_employee(self, employee_id: str) -> Optional[EmployeeDto]:
        emp = self._repo.find_by_id(employee_id)
        if not emp:
            return None
        return EmployeeDto(
            employee_id=emp.employee_id,
            name=emp.name,
            cpf=emp.cpf,
            role=emp.role,
            department=emp.department,
            base_salary=emp.base_salary,
            is_active=emp.is_active,
        )

    def list_active(self) -> List[EmployeeDto]:
        return [
            EmployeeDto(
                employee_id=e.employee_id,
                name=e.name,
                cpf=e.cpf,
                role=e.role,
                department=e.department,
                base_salary=e.base_salary,
                is_active=e.is_active,
            )
            for e in self._repo.list_all() if e.is_active
        ]
