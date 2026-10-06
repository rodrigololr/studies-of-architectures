"""Implementação Interna do Módulo TimeTracking (Schema: timetracking)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class _InternalTimesheet:
    timesheet_id: str
    employee_id: str
    month: str
    regular_hours: float
    overtime_hours: float
    absences_days: int
    is_closed: bool = True
    closed_at: datetime = field(default_factory=datetime.now)


class _InternalTimesheetRepository:
    def __init__(self) -> None:
        self._sheets: Dict[str, _InternalTimesheet] = {}

    def save(self, sheet: _InternalTimesheet) -> None:
        key = f"{sheet.employee_id}_{sheet.month}"
        self._sheets[key] = sheet

    def find(self, employee_id: str, month: str) -> Optional[_InternalTimesheet]:
        key = f"{employee_id}_{month}"
        return self._sheets.get(key)
