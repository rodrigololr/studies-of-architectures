"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de abertura, atribuição, resolução e encerramento de tickets,
convertendo violações de máquina de estados para HTTP 422 Unprocessable Entity.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import TicketService
from business.exceptions import (
    BusinessException,
    TicketNotFoundException,
    InvalidStatusTransitionException,
    TicketClosedException,
)
from data.models import TicketPriority


class TicketController:
    def __init__(self, service: TicketService) -> None:
        self.service = service

    def open_ticket(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/tickets"""
        try:
            priority = TicketPriority(payload.get("priority", "MEDIUM"))
            ticket = self.service.open_ticket(
                customer_id=payload.get("customer_id", ""),
                title=payload.get("title", ""),
                description=payload.get("description", ""),
                priority=priority,
            )
            return {
                "status_code": 201,
                "data": {
                    "ticket_id": ticket.ticket_id,
                    "title": ticket.title,
                    "priority": ticket.priority.value,
                    "status": ticket.status.value,
                    "sla_hours": ticket.sla_hours,
                },
            }
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def assign(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/tickets/{id}/assign"""
        try:
            agent_id = payload.get("agent_id", "")
            ticket = self.service.assign_agent(ticket_id, agent_id)
            return {
                "status_code": 200,
                "data": {"ticket_id": ticket.ticket_id, "status": ticket.status.value, "agent": ticket.assigned_agent},
            }
        except TicketNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except (InvalidStatusTransitionException, TicketClosedException) as ex:
            return {"status_code": 422, "error": str(ex)}

    def resolve(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/tickets/{id}/resolve"""
        try:
            notes = payload.get("notes", "Resolvido com sucesso")
            ticket = self.service.resolve_ticket(ticket_id, notes)
            return {
                "status_code": 200,
                "data": {"ticket_id": ticket.ticket_id, "status": ticket.status.value, "notes": ticket.resolution_notes},
            }
        except TicketNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except (InvalidStatusTransitionException, TicketClosedException) as ex:
            return {"status_code": 422, "error": str(ex)}

    def close(self, ticket_id: str) -> Dict[str, Any]:
        """POST /api/tickets/{id}/close"""
        try:
            ticket = self.service.close_ticket(ticket_id)
            return {
                "status_code": 200,
                "data": {"ticket_id": ticket.ticket_id, "status": ticket.status.value},
            }
        except TicketNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except (InvalidStatusTransitionException, TicketClosedException) as ex:
            return {"status_code": 422, "error": str(ex)}
