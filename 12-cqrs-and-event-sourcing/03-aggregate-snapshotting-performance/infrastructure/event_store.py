from typing import Dict, List
import copy
from domain.events import DomainEvent

class EventStore:
    """
    Event Store com suporte a leitura pontual a partir de versões específicas (Delta Read).
    """

    def __init__(self):
        self._streams: Dict[str, List[DomainEvent]] = {}

    def append_events(self, stream_id: str, events: List[DomainEvent]) -> None:
        stream = self._streams.setdefault(stream_id, [])
        for event in events:
            stream.append(event)

    def read_stream(self, stream_id: str) -> List[DomainEvent]:
        """Lê todos os eventos da stream desde a versão 1."""
        return [copy.deepcopy(e) for e in self._streams.get(stream_id, [])]

    def read_stream_from(self, stream_id: str, from_version: int) -> List[DomainEvent]:
        """
        Lê apenas os eventos com version >= from_version.
        Permite re-hidratação Delta após restauração de um Snapshot.
        """
        stream = self._streams.get(stream_id, [])
        filtered = [e for e in stream if e.version >= from_version]
        return [copy.deepcopy(e) for e in filtered]

    def get_version(self, stream_id: str) -> int:
        return len(self._streams.get(stream_id, []))
