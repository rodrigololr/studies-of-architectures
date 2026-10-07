from dataclasses import dataclass
import time
from typing import Any
from infrastructure.event_store import AppendOnlyEventStore

@dataclass(frozen=True)
class RebuildStats:
    events_replayed_count: int
    elapsed_ms: float
    projection_name: str

class ProjectionReplayEngine:
    """
    Motor de Reconstrução de Projeções (Zero-Downtime Event Replay).
    1. Replay integral da história de eventos desde o início dos tempos (offset 0).
    2. Subscrição contínua da projeção ao barramento do Event Store para receber eventos subsequentes.
    """

    def __init__(self, event_store: AppendOnlyEventStore):
        self._event_store = event_store

    def rebuild_and_subscribe(self, projection: Any) -> RebuildStats:
        start_time = time.perf_counter()

        # 1. Carrega o log global imutável desde o início
        all_events = self._event_store.get_all_events_ordered()

        # 2. Executa o replay histórico na nova projeção
        for event in all_events:
            projection.handle(event)

        # 3. Conecta a nova projeção ao fluxo contínuo de eventos em tempo real
        self._event_store.subscribe(projection.handle)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return RebuildStats(
            events_replayed_count=len(all_events),
            elapsed_ms=round(elapsed_ms, 4),
            projection_name=projection.__class__.__name__,
        )
