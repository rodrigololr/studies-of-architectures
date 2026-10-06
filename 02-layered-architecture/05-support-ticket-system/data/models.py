"""
models.py - Camada de Dados (Data Layer).
Modelos para representação de chamados de suporte, prioridades e estados do ticket.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


@dataclass
class TicketModel:
    ticket_id: str
    customer_id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    sla_hours: int
    assigned_agent: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: str = ""
    resolved_at: Optional[str] = None
