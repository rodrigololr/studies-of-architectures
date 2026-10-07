import sys
from pathlib import Path

# Inclusão do diretório para imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.event_store import AppendOnlyEventStore
from domain.aggregate import ProductAggregate
from projections.catalog_view import CurrentCatalogProjection
from projections.elasticity_analysis import PriceElasticityAndRefundProjection
from engine.replay_engine import ProjectionReplayEngine

def main():
    print("=" * 80)
    print("EXEMPLO 06: CQRS & EVENT SOURCING - EVENT REPLAY & PROJECTION REBUILD ENGINE")
    print("=" * 80)

    # 1. Inicializa o Event Store
    event_store = AppendOnlyEventStore()

    # 2. Inicializa a projeção legada (V1) e a conecta ao barramento
    legacy_catalog = CurrentCatalogProjection()
    event_store.subscribe(legacy_catalog.handle)

    print("\n[FASE 1] Histórico Operacional ao longo de 6 meses (Escritas no Event Store)...")
    p1 = ProductAggregate("PROD-HEADPHONE-01")
    p1.create(name="Fone Bluetooth Noise Cancelling", category="Eletrônicos", initial_price=500.0)

    # 10 compras ao preço de 500
    for i in range(1, 11):
        p1.record_purchase(order_id=f"ORD-500-{i}", quantity=1)

    # Aumento de preço para 650
    p1.change_price(new_price=650.0, reason="Aumento de custos de importação")

    # 4 compras ao preço de 650
    for i in range(1, 5):
        p1.record_purchase(order_id=f"ORD-650-{i}", quantity=1)

    # 1 devolução ao preço de 650 (insatisfação)
    p1.record_return(order_id="ORD-650-2", quantity=1, refund_amount=650.0, return_reason="Preço alto para o acabamento")

    # Promoção agressiva: redução para 450
    p1.change_price(new_price=450.0, reason="Promoção Black Friday")

    # 30 compras ao preço de 450
    for i in range(1, 31):
        p1.record_purchase(order_id=f"ORD-450-{i}", quantity=1)

    # 2 devoluções ao preço de 450
    p1.record_return(order_id="ORD-450-5", quantity=1, refund_amount=450.0, return_reason="Atraso na entrega")
    p1.record_return(order_id="ORD-450-8", quantity=1, refund_amount=450.0, return_reason="Defeito no cabo")

    # Persiste todos os eventos no Event Store
    event_store.append_events(p1.product_id, p1.uncommitted_events)
    p1.clear_uncommitted_events()

    # Segundo produto: Cadeira Ergonômica
    p2 = ProductAggregate("PROD-CHAIR-02")
    p2.create(name="Cadeira Ergonômica Mesh Pro", category="Mobiliário", initial_price=1800.0)
    for i in range(1, 6):
        p2.record_purchase(order_id=f"ORD-CHAIR-{i}", quantity=1)
    p2.change_price(new_price=2200.0, reason="Ajuste inflacionário")
    for i in range(6, 8):
        p2.record_purchase(order_id=f"ORD-CHAIR-{i}", quantity=1)

    event_store.append_events(p2.product_id, p2.uncommitted_events)
    p2.clear_uncommitted_events()

    print(f" -> Total de eventos gravados no Event Store global: {len(event_store.get_all_events_ordered())}")

    print("\n" + "=" * 80)
    print("PROJEÇÃO LEGADA V1 (CurrentCatalogProjection)")
    print("=" * 80)
    print("Na arquitetura CRUD original, apenas este resumo superficial estaria disponível:")
    for item in legacy_catalog.get_all():
        print(f"  • {item.name:<35} | Preço Atual: R$ {item.current_price:>8.2f} | Unidades Vendidas: {item.total_units_sold:>3}")

    print("\n" + "=" * 80)
    print("[FASE 2] NOVO REQUISITO DE NEGÓCIO: ANÁLISE DE ELASTICIDADE E DEVOLUÇÕES (V2)")
    print("=" * 80)
    print("Diretoria exige: 'Como as mudanças históricas de preço impactaram o volume e as devoluções?'")
    print("Iniciando o Projection Replay Engine para reconstruir a nova projeção do zero...")

    # Instancia o Replay Engine e a nova Projeção V2
    replay_engine = ProjectionReplayEngine(event_store)
    elasticity_projection = PriceElasticityAndRefundProjection()

    # Executa o Replay histórico e conecta ao barramento de eventos futuros
    stats = replay_engine.rebuild_and_subscribe(elasticity_projection)
    print(f"\n[REPLAY CONCLUÍDO COM SUCESSO]")
    print(f"  • Projeção Reconstruída: {stats.projection_name}")
    print(f"  • Eventos Re-processados: {stats.events_replayed_count} eventos históricos desde offset 0")
    print(f"  • Tempo de Rebuild:       {stats.elapsed_ms:.4f} ms (Zero Downtime no Write Side!)")

    print("\n" + "=" * 80)
    print("RESULTADO DA NOVA PROJEÇÃO V2 RECONSTRUÍDA A PARTIR DO PASSADO")
    print("=" * 80)

    for summary in elasticity_projection.get_all_summaries():
        print(f"\nProduto: {summary.product_name} ({summary.product_id})")
        print(f"  Reajustes de Preço:       {summary.price_changes_count}")
        print(f"  Vendas Brutas Totais:     {summary.total_units_sold} unidades (R$ {summary.total_gross_revenue:.2f})")
        print(f"  Devoluções Totais:        {summary.total_units_returned} unidades (R$ {summary.total_refunded_value:.2f})")
        print(f"  Taxa de Devolução Geral:  {summary.overall_return_rate_percent}%")
        print(f"  Faturamento Líquido Real: R$ {summary.net_revenue:.2f}")

        print("  Detalhamento por Faixa de Preço (Elasticidade):")
        print(f"    {'Preço Vigente':<16} | {'Vendas':<8} | {'Devoluções':<12} | {'Taxa Devolução':<16} | {'Receita Líquida'}")
        print("    " + "-" * 75)
        for price, tier in sorted(summary.tiers.items()):
            print(f"    R$ {price:>10.2f}    | {tier.units_sold:>6} | {tier.units_returned:>10} | {tier.return_rate_percent:>13.1f}% | R$ {tier.net_revenue:>12.2f}")

    print("\n" + "=" * 80)
    print("[FASE 3] VERIFICAÇÃO DE PROCESSAMENTO DE EVENTOS AO VIVO (LIVE STREAMING)")
    print("=" * 80)
    print("Simulando uma nova compra ocorrendo agora no sistema em produção...")

    # Realiza uma nova compra de 5 unidades do fone a R$ 450
    live_p1 = ProductAggregate(p1.product_id)
    live_p1.rehydrate(event_store.read_stream(p1.product_id))
    live_p1.record_purchase(order_id="ORD-LIVE-NEW-01", quantity=5)

    event_store.append_events(p1.product_id, live_p1.uncommitted_events)
    live_p1.clear_uncommitted_events()

    # Verifica se a nova projeção V2 recebeu a atualização automaticamente
    updated_summary = elasticity_projection.get_summary(p1.product_id)
    print(f" -> Nova Projeção V2 atualizada em tempo real:")
    print(f"    Unidades vendidas na faixa de R$ 450.00 aumentaram para: {updated_summary.tiers[450.0].units_sold} un")
    print(f"    Receita líquida total atualizada para: R$ {updated_summary.net_revenue:.2f}")
    assert updated_summary.tiers[450.0].units_sold == 35, "Deveria ter 35 unidades na faixa 450!"

    print("\n[OK] Rebuild de Projeção a partir de Event Replay comprovado com sucesso.")

if __name__ == "__main__":
    main()
