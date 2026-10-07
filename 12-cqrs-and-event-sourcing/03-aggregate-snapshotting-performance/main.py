import sys
from pathlib import Path
import random

# Inclusão do diretório para imports locais
sys.path.insert(0, str(Path(__file__).parent))

from domain.aggregate import PlayerAggregate
from infrastructure.event_store import EventStore
from infrastructure.snapshot_store import SnapshotStore
from infrastructure.repository import PlayerRepository

def main():
    print("=" * 80)
    print("EXEMPLO 03: CQRS & EVENT SOURCING - SNAPSHOTTING & OTIMIZAÇÃO DE PERFORMANCE")
    print("=" * 80)

    event_store = EventStore()
    snapshot_store = SnapshotStore()
    snapshot_interval = 50
    repository = PlayerRepository(event_store, snapshot_store, snapshot_interval=snapshot_interval)

    player_id = "PLAYER-WARRIOR-007"
    print(f"\n[PASSO 1] Criando e inicializando personagem '{player_id}'...")
    player = PlayerAggregate(player_id)
    player.spawn(player_name="Geralt de Rivia", max_health=100)
    repository.save(player)

    total_simulated_actions = 500
    print(f"[PASSO 2] Simulando sessão intensa de gameplay ({total_simulated_actions} ações em tempo real)...")

    # Gerador pseudo-aleatório com seed fixa para reprodutibilidade
    rng = random.Random(42)

    for i in range(1, total_simulated_actions):
        action_type = i % 4
        if action_type == 0:
            player.take_damage(damage_points=rng.randint(5, 25), attacker="Monstro do Pântano")
        elif action_type == 1:
            player.heal(heal_points=rng.randint(10, 30), source="Poção de Andorinha")
        elif action_type == 2:
            player.gain_xp(xp_points=rng.randint(80, 200))
        elif action_type == 3:
            player.loot_gold(amount=rng.randint(15, 60))

        # Salva em lotes de 50 ações
        if i % 50 == 0:
            repository.save(player)

    # Força salvamento das ações até aqui
    repository.save(player)

    # Executa 16 ações adicionais sem atingir o limiar de snapshot (50) para demonstrar o Delta Replay
    print(f"[PASSO 2.1] Executando 16 ações de combate adicionais pós-último snapshot...")
    for _ in range(16):
        player.gain_xp(xp_points=100)
        player.loot_gold(amount=25)
    # Persiste apenas os eventos no EventStore sem criar novo snapshot
    event_store.append_events(player.player_id, player.uncommitted_events)
    player.clear_uncommitted_events()

    total_events_in_stream = event_store.get_version(player_id)
    total_snapshots_saved = snapshot_store.get_snapshot_count(player_id)
    latest_snapshot = snapshot_store.get_latest_snapshot(player_id)

    print(f" -> Eventos totais gravados no stream: {total_events_in_stream}")
    print(f" -> Snapshots gerados no SnapshotStore: {total_snapshots_saved} (a cada {snapshot_interval} eventos)")
    if latest_snapshot:
        print(f" -> Último Snapshot gerado na versão: {latest_snapshot.version} (Nível: {latest_snapshot.level}, Ouro: {latest_snapshot.gold})")

    print("\n" + "=" * 80)
    print("[PASSO 3] BENCHMARK COMPARATIVO DE RE-HIDRATAÇÃO")
    print("=" * 80)

    # Executa 50 iterações de cada estratégia para obter médias estáveis
    iterations = 50

    # Teste 1: Full Replay
    total_time_full_ms = 0.0
    full_events_processed = 0
    full_agg = None
    for _ in range(iterations):
        agg, count, ms = repository.load_full_replay(player_id)
        total_time_full_ms += ms
        full_events_processed = count
        full_agg = agg
    avg_full_ms = total_time_full_ms / iterations

    # Teste 2: Snapshot + Delta
    total_time_snap_ms = 0.0
    snap_events_processed = 0
    snap_agg = None
    for _ in range(iterations):
        agg, count, ms = repository.load_with_snapshot(player_id)
        total_time_snap_ms += ms
        snap_events_processed = count
        snap_agg = agg
    avg_snap_ms = total_time_snap_ms / iterations

    print(f"Estratégia A: Full Replay (Sem Snapshots - O(N))")
    print(f"  • Eventos processados por carga:   {full_events_processed} eventos")
    print(f"  • Tempo médio por re-hidratação:   {avg_full_ms:.4f} ms")

    print(f"\nEstratégia B: Snapshotting + Delta Replay (O(N mod K))")
    print(f"  • Eventos processados por carga:   {snap_events_processed} eventos (apenas o Delta)")
    print(f"  • Tempo médio por re-hidratação:   {avg_snap_ms:.4f} ms")

    # Verificação de Redução de Eventos e Speedup
    event_reduction = ((full_events_processed - snap_events_processed) / full_events_processed) * 100.0
    print(f"\nResultados do Benchmark:")
    print(f"  • Redução de eventos processados:  {event_reduction:.1f}%")
    if avg_snap_ms > 0:
        speedup = avg_full_ms / avg_snap_ms
        print(f"  • Aceleração de Performance:       {speedup:.2f}x mais rápido")

    print("\n" + "=" * 80)
    print("[PASSO 4] VERIFICAÇÃO DE INTEGRIDADE E EQUIVALÊNCIA ESTRITA")
    print("=" * 80)

    assert full_agg.version == snap_agg.version, "Versões diferem!"
    assert full_agg.level == snap_agg.level, "Níveis diferem!"
    assert full_agg.health == snap_agg.health, "Pontos de vida diferem!"
    assert full_agg.max_health == snap_agg.max_health, "Max health difere!"
    assert full_agg.experience == snap_agg.experience, "Experiência difere!"
    assert full_agg.gold == snap_agg.gold, "Ouro difere!"

    print("Estado Final do Agregado verificado com sucesso:")
    print(f"  • Versão do Stream:  {snap_agg.version}")
    print(f"  • Nome do Jogador:   {snap_agg.player_name}")
    print(f"  • Nível Atual:       {snap_agg.level}")
    print(f"  • HP / HP Máximo:    {snap_agg.health} / {snap_agg.max_health}")
    print(f"  • Experiência (XP):  {snap_agg.experience}")
    print(f"  • Ouro Acumulado:    {snap_agg.gold}")
    print(f"  • Status de Vida:    {'VIVO' if snap_agg.is_alive else 'MORTO'}")

    print("\n[OK] Equivalência 100% comprovada entre Full Replay e Snapshotting.")

if __name__ == "__main__":
    main()
