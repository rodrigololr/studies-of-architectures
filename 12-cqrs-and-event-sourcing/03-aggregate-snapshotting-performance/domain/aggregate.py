from datetime import datetime
from typing import List, Optional
from domain.events import (
    DomainEvent,
    PlayerSpawned,
    DamageTaken,
    HealthRestored,
    ExperienceGained,
    LevelUpgraded,
    GoldLooted,
)
from domain.snapshot import PlayerSnapshot

class PlayerAggregate:
    """
    Agregado de Personagem de Jogos em Tempo Real.
    Suporta re-hidratação via replay de eventos e restauração otimizada via Snapshots.
    """

    def __init__(self, player_id: str):
        self.player_id: str = player_id
        self.player_name: str = ""
        self.level: int = 1
        self.health: int = 100
        self.max_health: int = 100
        self.experience: int = 0
        self.gold: int = 0
        self.is_alive: bool = True
        self.version: int = 0
        self._uncommitted_events: List[DomainEvent] = []

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # =========================================================================
    # RE-HIDRATAÇÃO E SNAPSHOTTING
    # =========================================================================

    def restore_from_snapshot(self, snapshot: PlayerSnapshot) -> None:
        """Restaura o estado diretamente de um instantâneo serializado em O(1)."""
        self.player_id = snapshot.aggregate_id
        self.player_name = snapshot.player_name
        self.level = snapshot.level
        self.health = snapshot.health
        self.max_health = snapshot.max_health
        self.experience = snapshot.experience
        self.gold = snapshot.gold
        self.is_alive = snapshot.is_alive
        self.version = snapshot.version
        self._uncommitted_events.clear()

    def create_snapshot(self) -> PlayerSnapshot:
        """Gera um snapshot imutável do estado corrente."""
        return PlayerSnapshot(
            aggregate_id=self.player_id,
            version=self.version,
            timestamp=datetime.utcnow(),
            player_name=self.player_name,
            level=self.level,
            health=self.health,
            max_health=self.max_health,
            experience=self.experience,
            gold=self.gold,
            is_alive=self.is_alive,
        )

    def rehydrate(self, events: List[DomainEvent]) -> None:
        """Aplica uma lista de eventos históricos sequencialmente."""
        for event in events:
            self._apply(event)
            self.version = event.version
        self._uncommitted_events.clear()

    def _record_that(self, event: DomainEvent) -> None:
        self._apply(event)
        self.version = event.version
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        self.version = event.version
        if isinstance(event, PlayerSpawned):
            self.player_name = event.player_name
            self.max_health = event.max_health
            self.health = event.max_health
            self.is_alive = True
        elif isinstance(event, DamageTaken):
            self.health = max(0, self.health - event.damage_points)
            if self.health == 0:
                self.is_alive = False
        elif isinstance(event, HealthRestored):
            if self.is_alive:
                self.health = min(self.max_health, self.health + event.heal_points)
        elif isinstance(event, ExperienceGained):
            self.experience += event.xp_points
        elif isinstance(event, LevelUpgraded):
            self.level = event.new_level
            self.max_health = event.new_max_health
            self.health = self.max_health  # cura completa ao subir de nível
        elif isinstance(event, GoldLooted):
            self.gold += event.amount

    # =========================================================================
    # AÇÕES DE DOMÍNIO
    # =========================================================================

    def spawn(self, player_name: str, max_health: int = 100) -> None:
        self._record_that(
            PlayerSpawned(
                aggregate_id=self.player_id,
                version=self.version + 1,
                player_name=player_name,
                max_health=max_health,
            )
        )

    def take_damage(self, damage_points: int, attacker: str = "Inimigo") -> None:
        if not self.is_alive:
            return
        if damage_points <= 0:
            return

        self._record_that(
            DamageTaken(
                aggregate_id=self.player_id,
                version=self.version + 1,
                damage_points=damage_points,
                attacker=attacker,
            )
        )

    def heal(self, heal_points: int, source: str = "Poção") -> None:
        if not self.is_alive or self.health >= self.max_health:
            return
        if heal_points <= 0:
            return

        self._record_that(
            HealthRestored(
                aggregate_id=self.player_id,
                version=self.version + 1,
                heal_points=heal_points,
                source=source,
            )
        )

    def gain_xp(self, xp_points: int) -> None:
        if not self.is_alive or xp_points <= 0:
            return

        self._record_that(
            ExperienceGained(
                aggregate_id=self.player_id,
                version=self.version + 1,
                xp_points=xp_points,
            )
        )

        # Regra de Level Up simples: cada 1000 XP ganha um novo nível
        target_level = 1 + (self.experience // 1000)
        if target_level > self.level:
            new_max = 100 + (target_level - 1) * 20
            self._record_that(
                LevelUpgraded(
                    aggregate_id=self.player_id,
                    version=self.version + 1,
                    new_level=target_level,
                    new_max_health=new_max,
                )
            )

    def loot_gold(self, amount: int) -> None:
        if not self.is_alive or amount <= 0:
            return

        self._record_that(
            GoldLooted(
                aggregate_id=self.player_id,
                version=self.version + 1,
                amount=amount,
            )
        )
