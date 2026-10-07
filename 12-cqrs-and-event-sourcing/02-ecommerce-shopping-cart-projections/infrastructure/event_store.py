from typing import Dict, List, Callable
import copy
from domain.events import DomainEvent
from domain.exceptions import ConcurrencyConflictException

class AppendOnlyEventStore:
    """
    Event Store Append-Only em memória com controle de versão otimista por stream.
    """

    def __init__(self):
        self._streams: Dict[str, List[DomainEvent]] = {}
        self._subscribers: List[Callable[[DomainEvent], None]] = []
        self._all_events: List[DomainEvent] = []

    def subscribe(self, subscriber: Callable[[DomainEvent], None]) -> None:
        self._subscribers.append(subscriber)

    def append_events(self, stream_id: str, events: List[DomainEvent], expected_version: int) -> None:
        if not events:
            return

        current_stream = self._streams.setdefault(stream_id, [])
        current_version = len(current_stream)

        if expected_version != current_version:
            raise ConcurrencyConflictException(
                f"Conflito de concorrência no carrinho '{stream_id}': "
                f"esperado={expected_version}, atual={current_version}"
            )

        for event in events:
            current_stream.append(event)
            self._all_events.append(event)

        for event in events:
            for sub in self._subscribers:
                sub(event)

    def read_stream(self, stream_id: str) -> List[DomainEvent]:
        events = self._streams.get(stream_id, [])
        return [copy.deepcopy(e) for e in events]

    def read_all(self) -> List[DomainEvent]:
        return [copy.deepcopy(e) for e in self._all_events]
