from typing import Dict, Optional
import copy
from domain.snapshot import PlayerSnapshot

class SnapshotStore:
    """
    Repositório de Snapshots em memória.
    Armazena o snapshot mais recente por agregado para recuperação instantânea em O(1).
    """

    def __init__(self):
        # aggregate_id -> PlayerSnapshot
        self._snapshots: Dict[str, PlayerSnapshot] = {}
        self._history: Dict[str, list[PlayerSnapshot]] = {}

    def save_snapshot(self, snapshot: PlayerSnapshot) -> None:
        self._snapshots[snapshot.aggregate_id] = copy.deepcopy(snapshot)
        self._history.setdefault(snapshot.aggregate_id, []).append(copy.deepcopy(snapshot))

    def get_latest_snapshot(self, aggregate_id: str) -> Optional[PlayerSnapshot]:
        snapshot = self._snapshots.get(aggregate_id)
        return copy.deepcopy(snapshot) if snapshot else None

    def get_snapshot_count(self, aggregate_id: str) -> int:
        return len(self._history.get(aggregate_id, []))
