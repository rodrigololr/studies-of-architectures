"""Ponto de Entrada e Facade do Módulo TimeTracking."""

import uuid
from shared.events import InProcessEventBus
from modules.timetracking.public_contracts import (
    ITimeTrackingModule,
    CloseTimesheetCommand,
    TimesheetSummaryDto,
    TimesheetClosedDomainEvent,
)
from modules.timetracking.internal.timetracking_internal import (
    _InternalTimesheet,
    _InternalTimesheetRepository,
)


class TimeTrackingModule(ITimeTrackingModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalTimesheetRepository()

    def close_month_timesheet(self, cmd: CloseTimesheetCommand) -> TimesheetSummaryDto:
        sheet_id = f"TS_{uuid.uuid4().hex[:8].upper()}"
        sheet = _InternalTimesheet(
            timesheet_id=sheet_id,
            employee_id=cmd.employee_id,
            month=cmd.month,
            regular_hours=cmd.regular_hours_worked,
            overtime_hours=cmd.overtime_hours,
            absences_days=cmd.unexcused_absences_days,
        )
        self._repo.save(sheet)

        # Publica evento para a folha de pagamento processar os reflexos financeiros
        self._bus.publish(TimesheetClosedDomainEvent(
            timesheet_id=sheet.timesheet_id,
            employee_id=sheet.employee_id,
            month=sheet.month,
            overtime_hours=sheet.overtime_hours,
            absences_days=sheet.absences_days,
        ))

        return TimesheetSummaryDto(
            timesheet_id=sheet.timesheet_id,
            employee_id=sheet.employee_id,
            month=sheet.month,
            regular_hours=sheet.regular_hours,
            overtime_hours=sheet.overtime_hours,
            absences_days=sheet.absences_days,
            is_closed=sheet.is_closed,
        )
