from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class PlayerSnapshot:
    """
    Representação serializada do estado acumulado de um jogador em determinada versão.
    """
    aggregate_id: str
    version: int
    timestamp: datetime
    player_name: str
    level: int
    health: int
    max_health: int
    experience: int
    gold: int
    is_alive: bool
