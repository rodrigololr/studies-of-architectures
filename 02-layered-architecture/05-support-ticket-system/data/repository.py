"""
repository.py - Camada de Dados (Data Layer).
Repositório de persistência de chamados com filtros de status e analista.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from data.models import TicketModel, TicketStatus


class TicketRepository:
    def __init__(self) -> None:
        self._table: Dict[str, TicketModel] = {}

    def save(self, ticket: TicketModel) -> TicketModel:
        self._table[ticket.ticket_id] = ticket
        return ticket

    def find_by_id(self, ticket_id: str) -> Optional[TicketModel]:
        return self._table.get(ticket_id)

    def list_by_status(self, status: TicketStatus) -> List[TicketModel]:
        return [t for t in self._table.values() if t.status == status]

    def list_by_agent(self, agent_id: str) -> List[TicketModel]:
        return [t for t in self._table.values() if t.assigned_agent == agent_id]
