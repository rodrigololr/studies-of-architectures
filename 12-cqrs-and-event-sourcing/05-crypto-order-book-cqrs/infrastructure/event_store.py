from typing import Dict, List, Callable
import copy
from domain.events import DomainEvent

class AppendOnlyEventStore:
    def __init__(self):
        self._streams: Dict[str, List[DomainEvent]] = {}
        self._subscribers: List[Callable[[DomainEvent], None]] = []
        self._log: List[DomainEvent] = []

    def subscribe(self, subscriber: Callable[[DomainEvent], None]) -> None:
        self._subscribers.append(subscriber)

    def append_events(self, stream_id: str, events: List[DomainEvent]) -> None:
        stream = self._streams.setdefault(stream_id, [])
        for e in events:
            stream.append(e)
            self._log.append(e)

        for e in events:
            for sub in self._subscribers:
                sub(e)

    def read_stream(self, stream_id: str) -> List[DomainEvent]:
        return [copy.deepcopy(e) for e in self._streams.get(stream_id, [])]

    def read_all(self) -> List[DomainEvent]:
        return [copy.deepcopy(e) for e in self._log]
