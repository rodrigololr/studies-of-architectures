import time
from typing import Tuple, Optional
from domain.aggregate import PlayerAggregate
from infrastructure.event_store import EventStore
from infrastructure.snapshot_store import SnapshotStore

class PlayerRepository:
    """
    Repositório de Agregado com suporte dual:
    1. Re-hidratação tradicional por Replay Total (O(N)).
    2. Re-hidratação acelerada via Snapshot + Delta Replay (O(N mod K)).
    """

    def __init__(self, event_store: EventStore, snapshot_store: SnapshotStore, snapshot_interval: int = 50):
        self._event_store = event_store
        self._snapshot_store = snapshot_store
        self._snapshot_interval = snapshot_interval

    def save(self, aggregate: PlayerAggregate) -> None:
        """Persiste eventos não comitados e gera snapshots periodicamente."""
        uncommitted = aggregate.uncommitted_events
        if not uncommitted:
            return

        self._event_store.append_events(aggregate.player_id, uncommitted)
        aggregate.clear_uncommitted_events()

        # Verifica se o agregado atingiu um ponto de corte para Snapshot
        last_snapshot = self._snapshot_store.get_latest_snapshot(aggregate.player_id)
        last_snap_version = last_snapshot.version if last_snapshot else 0

        if (aggregate.version - last_snap_version) >= self._snapshot_interval:
            snapshot = aggregate.create_snapshot()
            self._snapshot_store.save_snapshot(snapshot)

    def load_with_snapshot(self, player_id: str) -> Tuple[PlayerAggregate, int, float]:
        """
        Carrega o agregado utilizando o Snapshot mais recente + apenas os eventos Delta.
        Retorna: (instância_agregado, quantidade_de_eventos_processados, tempo_gasto_em_ms)
        """
        start_time = time.perf_counter()

        aggregate = PlayerAggregate(player_id)
        latest_snapshot = self._snapshot_store.get_latest_snapshot(player_id)

        events_replayed = 0
        if latest_snapshot:
            # 1. Restauração instantânea O(1)
            aggregate.restore_from_snapshot(latest_snapshot)
            # 2. Leitura apenas do Delta (versão snapshot + 1 em diante)
            delta_events = self._event_store.read_stream_from(player_id, latest_snapshot.version + 1)
            aggregate.rehydrate(delta_events)
            events_replayed = len(delta_events)
        else:
            # Sem snapshot prévio: replay total
            events = self._event_store.read_stream(player_id)
            aggregate.rehydrate(events)
            events_replayed = len(events)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return aggregate, events_replayed, elapsed_ms

    def load_full_replay(self, player_id: str) -> Tuple[PlayerAggregate, int, float]:
        """
        Ignora deliberadamente quaisquer snapshots e faz o replay integral de TODOS os eventos do stream.
        Utilizado para benchmarking comparativo.
        """
        start_time = time.perf_counter()

        aggregate = PlayerAggregate(player_id)
        all_events = self._event_store.read_stream(player_id)
        aggregate.rehydrate(all_events)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return aggregate, len(all_events), elapsed_ms
