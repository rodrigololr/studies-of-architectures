"""Contrato Público do Módulo TimeTracking (Ponto Eletrônico e Horas Trabalhadas)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from shared.events import DomainEvent


@dataclass(frozen=True)
class CloseTimesheetCommand:
    employee_id: str
    month: str  # ex: "2026-05"
    regular_hours_worked: float
    overtime_hours: float
    unexcused_absences_days: int


@dataclass(frozen=True)
class TimesheetSummaryDto:
    timesheet_id: str
    employee_id: str
    month: str
    regular_hours: float
    overtime_hours: float
    absences_days: int
    is_closed: bool


@dataclass(frozen=True)
class TimesheetClosedDomainEvent(DomainEvent):
    """Evento emitido ao término do fechamento do espelho de ponto mensal."""
    timesheet_id: str = ""
    employee_id: str = ""
    month: str = ""
    overtime_hours: float = 0.0
    absences_days: int = 0


class ITimeTrackingModule(ABC):
    @abstractmethod
    def close_month_timesheet(self, cmd: CloseTimesheetCommand) -> TimesheetSummaryDto:
        pass
