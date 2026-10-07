from typing import Dict, List, Callable
import copy
from domain.events import DomainEvent
from domain.exceptions import ConcurrencyConflictException

class AppendOnlyEventStore:
    """
    Event Store Append-Only em memória com suporte a:
    1. Streams isolados por agregado.
    2. Controle de Concorrência Otimista (OCC via expected_version).
    3. Barramento de publicação síncrona para projetores (Read Side).
    """

    def __init__(self):
        # Mapeamento: stream_id -> lista sequencial de eventos imutáveis
        self._streams: Dict[str, List[DomainEvent]] = {}
        # Assinantes para projeções
        self._subscribers: List[Callable[[DomainEvent], None]] = []
        # Histórico global em ordem de inserção
        self._global_log: List[DomainEvent] = []

    def subscribe(self, subscriber: Callable[[DomainEvent], None]) -> None:
        """Registra um projetor para receber eventos à medida que são comitados."""
        self._subscribers.append(subscriber)

    def get_stream_version(self, stream_id: str) -> int:
        stream = self._streams.get(stream_id, [])
        return len(stream)

    def append_events(self, stream_id: str, events: List[DomainEvent], expected_version: int) -> None:
        """
        Adiciona eventos ao stream com verificação estrita de controle de concorrência otimista.
        """
        if not events:
            return

        current_stream = self._streams.setdefault(stream_id, [])
        current_version = len(current_stream)

        # Verificação atômica de concorrência
        if expected_version != current_version:
            raise ConcurrencyConflictException(
                f"Conflito de concorrência no stream '{stream_id}': "
                f"versão esperada={expected_version}, versão atual no banco={current_version}"
            )

        # Gravação atômica
        for event in events:
            current_stream.append(event)
            self._global_log.append(event)

        # Despacho para projetores (Read Side)
        for event in events:
            for subscriber in self._subscribers:
                subscriber(event)

    def read_stream(self, stream_id: str) -> List[DomainEvent]:
        """Lê todos os eventos de um stream em ordem estritamente cronológica."""
        events = self._streams.get(stream_id, [])
        return [copy.deepcopy(e) for e in events]

    def read_all_events(self) -> List[DomainEvent]:
        """Retorna o log global para auditoria ou replay total de projeções."""
        return [copy.deepcopy(e) for e in self._global_log]
