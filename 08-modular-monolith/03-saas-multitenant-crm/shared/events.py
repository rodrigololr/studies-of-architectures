"""Shared Kernel: Barramento de Eventos em Memória (In-Process Event Bus)."""

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Dict, List, Type, Callable, Any


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    tenant_id: str = ""

    @property
    def event_name(self) -> str:
        return self.__class__.__name__


EventHandler = Callable[[Any], None]


class InProcessEventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}
        self.published_events: List[DomainEvent] = []

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
        for handler in self._handlers.get(type(event), []):
            handler(event)
