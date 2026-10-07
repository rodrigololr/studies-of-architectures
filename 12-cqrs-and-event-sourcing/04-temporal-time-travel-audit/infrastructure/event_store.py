from datetime import datetime
from typing import Dict, List
import copy
from domain.events import DomainEvent

class AppendOnlyEventStore:
    """
    Event Store com suporte nativo a consultas temporais ("As-Of" Queries).
    """

    def __init__(self):
        self._streams: Dict[str, List[DomainEvent]] = {}

    def append_events(self, stream_id: str, events: List[DomainEvent]) -> None:
        stream = self._streams.setdefault(stream_id, [])
        for e in events:
            stream.append(e)

    def read_stream(self, stream_id: str) -> List[DomainEvent]:
        """Retorna o stream integral até o momento presente."""
        return [copy.deepcopy(e) for e in self._streams.get(stream_id, [])]

    def read_stream_as_of(self, stream_id: str, as_of: datetime) -> List[DomainEvent]:
        """
        Retorna apenas os eventos ocorridos estritamente ATÉ o carimbo de data/hora 'as_of'.
        Permite reconstruir fielmente o passado (Viagem no Tempo).
        """
        stream = self._streams.get(stream_id, [])
        filtered = [e for e in stream if e.timestamp <= as_of]
        return [copy.deepcopy(e) for e in filtered]

    def read_all(self) -> List[DomainEvent]:
        all_events = []
        for s in self._streams.values():
            all_events.extend(s)
        all_events.sort(key=lambda e: e.timestamp)
        return [copy.deepcopy(e) for e in all_events]
