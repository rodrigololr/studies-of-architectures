from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from domain.aggregate import EmployeeAggregate
from infrastructure.event_store import AppendOnlyEventStore
from domain.events import (
    EmployeeHired,
    DepartmentTransferred,
    SalaryAdjusted,
    RolePromoted,
    BonusAwarded,
)

@dataclass(frozen=True)
class EmployeeHistoricalSnapshot:
    employee_id: str
    as_of: datetime
    exists: bool
    full_name: str
    role: str
    department: str
    salary: float
    rank_level: int
    total_bonuses: float
    events_replayed_count: int

class TimeTravelAuditService:
    """
    Motor de Auditoria Temporal.
    Permite responder a qualquer questionamento de conformidade fiscal/trabalhista
    sobre o estado exato de um colaborador em qualquer carimbo de data no passado.
    """

    def __init__(self, event_store: AppendOnlyEventStore):
        self._event_store = event_store

    def get_employee_state_as_of(self, employee_id: str, as_of: datetime) -> EmployeeHistoricalSnapshot:
        events = self._event_store.read_stream_as_of(employee_id, as_of)
        if not events:
            return EmployeeHistoricalSnapshot(
                employee_id=employee_id,
                as_of=as_of,
                exists=False,
                full_name="",
                role="",
                department="",
                salary=0.0,
                rank_level=0,
                total_bonuses=0.0,
                events_replayed_count=0,
            )

        aggregate = EmployeeAggregate(employee_id)
        aggregate.rehydrate(events)

        return EmployeeHistoricalSnapshot(
            employee_id=employee_id,
            as_of=as_of,
            exists=True,
            full_name=aggregate.full_name,
            role=aggregate.role,
            department=aggregate.department,
            salary=aggregate.salary,
            rank_level=aggregate.rank_level,
            total_bonuses=aggregate.total_bonuses,
            events_replayed_count=len(events),
        )

    def get_audit_timeline(self, employee_id: str) -> List[dict]:
        events = self._event_store.read_stream(employee_id)
        timeline = []
        for e in events:
            desc = ""
            if isinstance(e, EmployeeHired):
                desc = f"Contratação: {e.role} em {e.department} (Salário Inicial: R$ {e.salary:.2f})"
            elif isinstance(e, DepartmentTransferred):
                desc = f"Transferência: de '{e.previous_department}' para '{e.new_department}' ({e.reason})"
            elif isinstance(e, SalaryAdjusted):
                diff = e.new_salary - e.previous_salary
                pct = (diff / e.previous_salary * 100.0) if e.previous_salary > 0 else 0.0
                desc = f"Ajuste Salarial: R$ {e.previous_salary:.2f} -> R$ {e.new_salary:.2f} (+{pct:.1f}%) | Motivo: {e.justification}"
            elif isinstance(e, RolePromoted):
                desc = f"Promoção de Cargo: '{e.previous_role}' -> '{e.new_role}' (Nível de Senioridade: {e.rank_level})"
            elif isinstance(e, BonusAwarded):
                desc = f"Bônus de Desempenho Concedido: R$ {e.amount:.2f} ({e.reason})"

            timeline.append({
                "version": e.version,
                "timestamp": e.timestamp.strftime("%Y-%m-%d"),
                "event_type": e.__class__.__name__,
                "description": desc,
            })
        return timeline
