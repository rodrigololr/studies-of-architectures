from datetime import datetime
from typing import List, Optional
from domain.events import (
    DomainEvent,
    EmployeeHired,
    DepartmentTransferred,
    SalaryAdjusted,
    RolePromoted,
    BonusAwarded,
)

class EmployeeAggregate:
    """
    Agregado de Colaborador / Histórico Funcional de RH.
    Suporta re-hidratação total ou temporal (até timestamp T).
    """

    def __init__(self, employee_id: str):
        self.employee_id: str = employee_id
        self.full_name: str = ""
        self.role: str = ""
        self.department: str = ""
        self.salary: float = 0.0
        self.rank_level: int = 1
        self.total_bonuses: float = 0.0
        self.is_active: bool = False
        self.version: int = 0
        self.last_updated: Optional[datetime] = None
        self._uncommitted_events: List[DomainEvent] = []

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # =========================================================================
    # RE-HIDRATAÇÃO
    # =========================================================================

    def rehydrate(self, events: List[DomainEvent]) -> None:
        for event in events:
            self._apply(event)
        self._uncommitted_events.clear()

    def _record_that(self, event: DomainEvent) -> None:
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        self.version = event.version
        self.last_updated = event.timestamp

        if isinstance(event, EmployeeHired):
            self.full_name = event.full_name
            self.role = event.role
            self.department = event.department
            self.salary = event.salary
            self.is_active = True
        elif isinstance(event, DepartmentTransferred):
            self.department = event.new_department
        elif isinstance(event, SalaryAdjusted):
            self.salary = event.new_salary
        elif isinstance(event, RolePromoted):
            self.role = event.new_role
            self.rank_level = event.rank_level
        elif isinstance(event, BonusAwarded):
            self.total_bonuses += event.amount

    # =========================================================================
    # OPERAÇÕES DE NEGÓCIO
    # =========================================================================

    def hire(self, timestamp: datetime, full_name: str, role: str, department: str, salary: float) -> None:
        if self.is_active:
            raise ValueError(f"Colaborador {self.employee_id} já contratado.")
        self._record_that(
            EmployeeHired(
                aggregate_id=self.employee_id,
                version=self.version + 1,
                timestamp=timestamp,
                full_name=full_name,
                role=role,
                department=department,
                salary=salary,
            )
        )

    def transfer_department(self, timestamp: datetime, new_department: str, reason: str) -> None:
        if not self.is_active:
            raise ValueError("Colaborador inativo.")
        if self.department == new_department:
            return

        self._record_that(
            DepartmentTransferred(
                aggregate_id=self.employee_id,
                version=self.version + 1,
                timestamp=timestamp,
                previous_department=self.department,
                new_department=new_department,
                reason=reason,
            )
        )

    def adjust_salary(self, timestamp: datetime, new_salary: float, justification: str) -> None:
        if not self.is_active:
            raise ValueError("Colaborador inativo.")
        if new_salary <= 0:
            raise ValueError("Salário deve ser maior que zero.")

        self._record_that(
            SalaryAdjusted(
                aggregate_id=self.employee_id,
                version=self.version + 1,
                timestamp=timestamp,
                previous_salary=self.salary,
                new_salary=new_salary,
                justification=justification,
            )
        )

    def promote(self, timestamp: datetime, new_role: str, rank_level: int) -> None:
        if not self.is_active:
            raise ValueError("Colaborador inativo.")
        self._record_that(
            RolePromoted(
                aggregate_id=self.employee_id,
                version=self.version + 1,
                timestamp=timestamp,
                previous_role=self.role,
                new_role=new_role,
                rank_level=rank_level,
            )
        )

    def award_bonus(self, timestamp: datetime, amount: float, reason: str) -> None:
        if not self.is_active:
            raise ValueError("Colaborador inativo.")
        if amount <= 0:
            raise ValueError("Valor de bônus deve ser positivo.")

        self._record_that(
            BonusAwarded(
                aggregate_id=self.employee_id,
                version=self.version + 1,
                timestamp=timestamp,
                amount=amount,
                reason=reason,
            )
        )
