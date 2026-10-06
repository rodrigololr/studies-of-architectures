"""
service.py - Camada de Negócio (Business Layer).

Responsável por:
- Calcular horas de SLA baseado na criticidade do ticket.
- Atribuir chamado a um analista (movendo status para IN_PROGRESS).
- Garantir transições válidas na máquina de estados (OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED).
- Bloquear alterações após fechamento definitivo.
"""

from __future__ import annotations
from datetime import datetime
import uuid
from typing import Dict, List, Optional
from business.exceptions import (
    TicketNotFoundException,
    InvalidStatusTransitionException,
    TicketClosedException,
)
from data.models import TicketModel, TicketPriority, TicketStatus
from data.repository import TicketRepository


class TicketService:
    SLA_MATRIX: Dict[TicketPriority, int] = {
        TicketPriority.CRITICAL: 2,   # 2 horas para incidentes críticos
        TicketPriority.HIGH: 8,       # 8 horas
        TicketPriority.MEDIUM: 24,    # 24 horas
        TicketPriority.LOW: 72,       # 72 horas
    }

    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    def open_ticket(
        self, customer_id: str, title: str, description: str, priority: TicketPriority
    ) -> TicketModel:
        sla_hours = self.SLA_MATRIX.get(priority, 24)
        ticket = TicketModel(
            ticket_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            status=TicketStatus.OPEN,
            sla_hours=sla_hours,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return self.repository.save(ticket)

    def assign_agent(self, ticket_id: str, agent_id: str) -> TicketModel:
        ticket = self._get_ticket_or_fail(ticket_id)
        if ticket.status == TicketStatus.CLOSED:
            raise TicketClosedException("Não é possível alterar chamados já encerrados.")

        ticket.assigned_agent = agent_id
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS

        return self.repository.save(ticket)

    def resolve_ticket(self, ticket_id: str, resolution_notes: str) -> TicketModel:
        ticket = self._get_ticket_or_fail(ticket_id)
        if ticket.status == TicketStatus.CLOSED:
            raise TicketClosedException("O chamado já está encerrado.")

        if ticket.status == TicketStatus.OPEN:
            raise InvalidStatusTransitionException(
                "Um chamado não pode ser resolvido diretamente sem antes ser atribuído e colocado em andamento."
            )

        ticket.status = TicketStatus.RESOLVED
        ticket.resolution_notes = resolution_notes
        ticket.resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.repository.save(ticket)

    def close_ticket(self, ticket_id: str) -> TicketModel:
        ticket = self._get_ticket_or_fail(ticket_id)
        if ticket.status != TicketStatus.RESOLVED:
            raise InvalidStatusTransitionException(
                f"Apenas chamados no estado RESOLVED podem ser fechados. Estado atual: '{ticket.status.value}'."
            )

        ticket.status = TicketStatus.CLOSED
        return self.repository.save(ticket)

    def _get_ticket_or_fail(self, ticket_id: str) -> TicketModel:
        ticket = self.repository.find_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException(f"Chamado com ID '{ticket_id}' não encontrado.")
        return ticket
