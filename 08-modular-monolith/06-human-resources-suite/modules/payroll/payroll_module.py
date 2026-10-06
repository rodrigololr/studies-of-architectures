"""Ponto de Entrada e Facade do Módulo Payroll."""

import uuid
from typing import Optional, List
from shared.events import InProcessEventBus
from modules.employees.public_contracts import IEmployeeModule
from modules.timetracking.public_contracts import TimesheetClosedDomainEvent
from modules.payroll.public_contracts import IPayrollModule, PayslipDto
from modules.payroll.internal.payroll_internal import (
    _InternalPayslip,
    _InternalPayrollRepository,
)


class PayrollModule(IPayrollModule):
    def __init__(
        self,
        employees_module: IEmployeeModule,
        event_bus: InProcessEventBus,
    ) -> None:
        self._employees = employees_module
        self._bus = event_bus
        self._repo = _InternalPayrollRepository()

        # Reage ao fechamento do espelho de ponto para calcular os reflexos em folha
        self._bus.subscribe(TimesheetClosedDomainEvent, self._handle_timesheet_closed)

    def _handle_timesheet_closed(self, e: TimesheetClosedDomainEvent) -> None:
        emp = self._employees.get_employee(e.employee_id)
        if not emp:
            return

        base_sal = emp.base_salary
        hourly_rate = base_sal / 220.0
        daily_rate = base_sal / 30.0

        # Hora extra com adicional constitucional de 50%
        overtime_val = round(e.overtime_hours * hourly_rate * 1.50, 2)
        # Desconto de faltas injustificadas
        absence_val = round(e.absences_days * daily_rate, 2)

        net_val = round(base_sal + overtime_val - absence_val, 2)

        ps_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        ps = _InternalPayslip(
            payslip_id=ps_id,
            employee_id=e.employee_id,
            month=e.month,
            base_salary=base_sal,
            overtime_pay=overtime_val,
            absence_deduction=absence_val,
            net_salary=net_val,
        )
        self._repo.save(ps)

    def get_payslip(self, employee_id: str, month: str) -> Optional[PayslipDto]:
        ps = self._repo.find(employee_id, month)
        if not ps:
            return None
        return PayslipDto(
            payslip_id=ps.payslip_id,
            employee_id=ps.employee_id,
            month=ps.month,
            base_salary=ps.base_salary,
            overtime_pay=ps.overtime_pay,
            absence_deduction=ps.absence_deduction,
            net_salary=ps.net_salary,
        )

    def list_month(self, month: str) -> List[PayslipDto]:
        return [
            PayslipDto(
                payslip_id=p.payslip_id,
                employee_id=p.employee_id,
                month=p.month,
                base_salary=p.base_salary,
                overtime_pay=p.overtime_pay,
                absence_deduction=p.absence_deduction,
                net_salary=p.net_salary,
            )
            for p in self._repo.list_by_month(month)
        ]
