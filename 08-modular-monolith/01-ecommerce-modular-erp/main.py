"""Ponto de Entrada e Demonstração Executável - Exemplo 01: E-Commerce Modular ERP.

Demonstra:
1. Composição de módulos estritamente isolados em um processo único (Monólito Modular).
2. Comunicação entre módulos via Contratos Públicos (Interfaces e DTOs).
3. Barramento de Eventos intra-processo (In-Process Event Bus / Mediator).
4. Compensação atômica de estoque em caso de falha de pagamento.
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.catalog import CatalogModule
from modules.inventory import InventoryModule
from modules.payments import PaymentsModule
from modules.orders import (
    OrdersModule,
    PlaceOrderCommand,
    OrderItemInputDto,
    OrderPlacedDomainEvent,
    OrderCancelledDomainEvent,
)
from modules.payments.public_contracts import (
    PaymentSucceededDomainEvent,
    PaymentFailedDomainEvent,
)


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 01: E-COMMERCE MODULAR ERP")
    print("=" * 80)

    # 1. Instanciação da Infraestrutura Compartilhada (Shared Kernel)
    event_bus = InProcessEventBus()

    # Log de eventos em tempo real
    event_bus.subscribe(OrderPlacedDomainEvent, lambda e: print(
        f"  [EVENT BUS -> AUDIT] Evento '{e.event_name}': Pedido #{e.order_id} criado no valor de R$ {e.total_amount:,.2f}"
    ))
    event_bus.subscribe(PaymentSucceededDomainEvent, lambda e: print(
        f"  [EVENT BUS -> FINANCE] Evento '{e.event_name}': Pagamento aprovado para #{e.order_id} (TX: {e.transaction_id})"
    ))
    event_bus.subscribe(PaymentFailedDomainEvent, lambda e: print(
        f"  [EVENT BUS -> ALERTA] Evento '{e.event_name}': Pagamento falhou para #{e.order_id}. Motivo: {e.reason}"
    ))
    event_bus.subscribe(OrderCancelledDomainEvent, lambda e: print(
        f"  [EVENT BUS -> ESTOQUE] Evento '{e.event_name}': Pedido #{e.order_id} cancelado. Motivo: {e.reason}"
    ))

    # 2. Inicialização dos Módulos Independentes
    catalog = CatalogModule()
    inventory = InventoryModule(event_bus=event_bus)
    payments = PaymentsModule(event_bus=event_bus)
    orders = OrdersModule(
        catalog_module=catalog,
        inventory_module=inventory,
        payments_module=payments,
        event_bus=event_bus,
    )

    # 3. Carga Inicial de Dados (Seed por Módulo)
    print("\n--- 1. Carga Inicial de Catálogo e Estoque ---")
    catalog.seed_product("P1", "NOTE-DELL-XPS", "Notebook Dell XPS 13", cost=6000.0, price=9500.0)
    catalog.seed_product("P2", "MOUSE-LOGI-MX", "Mouse Logitech MX Master 3", cost=300.0, price=550.0)
    catalog.seed_product("P3", "MONITOR-4K-27", "Monitor Dell UltraSharp 27 4K", cost=1800.0, price=2800.0)

    inventory.seed_stock("NOTE-DELL-XPS", quantity=5)
    inventory.seed_stock("MOUSE-LOGI-MX", quantity=10)
    inventory.seed_stock("MONITOR-4K-27", quantity=2)

    for prod in catalog.list_catalog():
        saldo = inventory.check_availability(prod.sku)
        print(f" -> Produto: {prod.name} | SKU: {prod.sku} | Preço: R$ {prod.price:,.2f} | Saldo: {saldo} un.")

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Pedido Válido com Sucesso Completo (Happy Path)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Pedido Concluído e Faturado (1x Dell XPS + 1x Mouse MX) ---")
    res_1 = orders.place_order(PlaceOrderCommand(
        customer_name="Roberto Justos",
        customer_email="roberto@empresa.com",
        payment_method="CREDIT_CARD",
        items=[
            OrderItemInputDto(sku="NOTE-DELL-XPS", quantity=1),
            OrderItemInputDto(sku="MOUSE-LOGI-MX", quantity=1),
        ],
    ))
    print(f"Status: {res_1.status} | Total: R$ {res_1.total_amount:,.2f} | Msg: {res_1.message}")
    print(f"Saldos pós-compra: Dell XPS={inventory.check_availability('NOTE-DELL-XPS')} un | Mouse={inventory.check_availability('MOUSE-LOGI-MX')} un")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Rejeição Imediata por Falta de Estoque
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Tentativa de Compra com Estoque Insuficiente (5 Monitores quando só há 2) ---")
    res_2 = orders.place_order(PlaceOrderCommand(
        customer_name="Beatriz Souza",
        customer_email="beatriz@design.com",
        payment_method="PIX",
        items=[
            OrderItemInputDto(sku="MONITOR-4K-27", quantity=5),
        ],
    ))
    print(f"Status: {res_2.status} | Msg: {res_2.message}")
    print(f"Saldo Monitor 4K permanece inalterado: {inventory.check_availability('MONITOR-4K-27')} un.")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Falha de Pagamento com Compensação Automática de Estoque
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Pagamento Recusado e Desfazimento Atômico da Reserva de Estoque ---")
    # Cliente simula recusa no cartão
    saldo_antes_xps = inventory.check_availability("NOTE-DELL-XPS")
    res_3 = orders.place_order(PlaceOrderCommand(
        customer_name="Carlos Fraude",
        customer_email="cartao.recusado@test.com",
        payment_method="CREDIT_CARD",
        items=[
            OrderItemInputDto(sku="NOTE-DELL-XPS", quantity=2),
        ],
    ))
    print(f"Status: {res_3.status} | Msg: {res_3.message}")
    saldo_depois_xps = inventory.check_availability("NOTE-DELL-XPS")
    print(f"Verificação de Compensação: Saldo antes={saldo_antes_xps} un | Saldo depois={saldo_depois_xps} un (Estoque preservado!)")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Tentativa com SKU Inexistente no Catálogo
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Produto Não Cadastrado no Catálogo ---")
    res_4 = orders.place_order(PlaceOrderCommand(
        customer_name="Juliana Paes",
        customer_email="juliana@gmail.com",
        payment_method="PIX",
        items=[
            OrderItemInputDto(sku="TECLADO-MECANICO-RGB", quantity=1),
        ],
    ))
    print(f"Status: {res_4.status} | Msg: {res_4.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Resumo e Auditoria de Eventos Disparados no Monólito
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Auditoria do Barramento de Eventos (Event Bus History) ---")
    print(f"Total de eventos de domínio trafegados na memória do processo: {len(event_bus.published_history)}")
    for idx, ev in enumerate(event_bus.published_history, start=1):
        print(f"  {idx}. [{ev.occurred_at.strftime('%H:%M:%S')}] {ev.event_name} (ID: {ev.event_id[:8]})")

    print("\n" + "=" * 80)
    print(" Exemplo 01 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
