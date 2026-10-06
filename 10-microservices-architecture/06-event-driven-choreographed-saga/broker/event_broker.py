"""In-Memory Message Broker assíncrono para publicação e assinatura de eventos de domínio."""

from typing import Dict, List, Callable, Type, Any
from broker.domain_events import DomainEvent


class InMemoryEventBroker:
    """Barramento de mensageria leve (Kafka/RabbitMQ simulator)."""

    def __init__(self) -> None:
        self._subscribers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self._event_history: List[DomainEvent] = []

    def subscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[Any], None]
    ) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        self._event_history.append(event)
        event_cls = type(event)
        handlers = self._subscribers.get(event_cls, [])
        for handler in handlers:
            handler(event)

    @property
    def event_history(self) -> List[DomainEvent]:
        return list(self._event_history)

    def clear_history(self) -> None:
        self._event_history.clear()
