from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class PlayerSpawned(DomainEvent):
    player_name: str = ""
    max_health: int = 100

@dataclass(frozen=True)
class DamageTaken(DomainEvent):
    damage_points: int = 0
    attacker: str = ""

@dataclass(frozen=True)
class HealthRestored(DomainEvent):
    heal_points: int = 0
    source: str = ""

@dataclass(frozen=True)
class ExperienceGained(DomainEvent):
    xp_points: int = 0

@dataclass(frozen=True)
class LevelUpgraded(DomainEvent):
    new_level: int = 1
    new_max_health: int = 100

@dataclass(frozen=True)
class GoldLooted(DomainEvent):
    amount: int = 0
