"""Shared Kernel: Barramento de Eventos em Memória (In-Process Event Bus / Mediator).

Permite a comunicação reativa e fracamente acoplada entre os módulos do monólito
sem que eles precisem se referenciar diretamente ou compartilhar modelos internos.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Dict, List, Type, Callable, Any


@dataclass(frozen=True)
class DomainEvent:
    """Evento base do domínio."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__


EventHandler = Callable[[Any], None]


class InProcessEventBus:
    """Mediator / Barramento em memória no mesmo processo do Monólito."""
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}
        self.published_history: List[DomainEvent] = []

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Registra um módulo como ouvinte de um evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Dispara o evento para todos os ouvintes inscritos de maneira síncrona/em processo."""
        self.published_history.append(event)
        event_cls = type(event)
        handlers = self._handlers.get(event_cls, [])
        for handler in handlers:
            handler(event)
