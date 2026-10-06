"""Demonstração de Microsserviços: Saga Coreografada Reativa via Eventos (Sem Orquestrador Central).

Cenários demonstrados:
1. Caminho Feliz Coreografado: Cada microsserviço reage a eventos e avança a cadeia até a confirmação
2. Falha de Pagamento: Emissão de evento de falha cancela o pedido de forma reativa
3. Falha de Estoque: Emissão de evento de falha dispara compensação automática de estorno no pagamento
4. Falha na Entrega: Compensação em cadeia reativa (Estoque liberado -> Pagamento estornado -> Pedido cancelado)
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from broker.event_broker import InMemoryEventBroker
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.inventory_service import InventoryService
from services.delivery_service import DeliveryService


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def print_event_timeline(broker: InMemoryEventBroker, order_id: str) -> None:
    events = [e for e in broker.event_history if e.order_id == order_id]
    print(f"\nLinha do Tempo de Eventos de Domínio no Broker (Pedido: {order_id}):")
    for i, ev in enumerate(events, 1):
        event_name = type(ev).__name__
        reason = getattr(ev, "reason", "")
        reason_str = f" | Motivo: {reason}" if reason else ""
        print(f"  {i}. [EVENT-BUS] ➔ {event_name:<26} {reason_str}")


def main() -> None:
    print("Inicializando Ecossistema de Microsserviços Orientado a Eventos (Saga Coreografada)...")

    # Barramento de mensageria assíncrono comum a todos os microsserviços
    broker = InMemoryEventBroker()

    # Inicialização dos 4 Microsserviços autônomos
    order_svc = OrderService(broker)
    payment_svc = PaymentService(broker)
    inventory_svc = InventoryService(broker)
    delivery_svc = DeliveryService(broker)

    # -------------------------------------------------------------------------
    # Cenário 1: Caminho Feliz (Compra de TV OLED)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Compra Concluída com Sucesso (Coreografia sem Orquestrador)")
    order_svc.place_order(
        order_id="ORD-CHOREO-01",
        customer_id="CUST-ALICE",
        amount=4200.0,
        items=(("SKU-TV-OLED", 1),),
        shipping_postal_code="04538-133",
    )
    status1 = order_svc.get_order_status("ORD-CHOREO-01")
    print(f"Status Final do Pedido no OrderService: {status1}")
    print_event_timeline(broker, "ORD-CHOREO-01")
    assert status1 == "CONFIRMED"

    # -------------------------------------------------------------------------
    # Cenário 2: Falha no Pagamento (Bob com Crédito Insuficiente)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Falha de Pagamento e Cancelamento Reativo")
    order_svc.place_order(
        order_id="ORD-CHOREO-02",
        customer_id="CUST-BOB",
        amount=4200.0,
        items=(("SKU-TV-OLED", 1),),
        shipping_postal_code="04538-133",
    )
    status2 = order_svc.get_order_status("ORD-CHOREO-02")
    print(f"Status Final do Pedido no OrderService: {status2}")
    print_event_timeline(broker, "ORD-CHOREO-02")
    assert status2 == "CANCELLED"

    # -------------------------------------------------------------------------
    # Cenário 3: Falha no Estoque (Console Esgotado) -> Estorno Reativo
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Falha no Estoque desencadeando Estorno no Microsserviço de Pagamento")
    order_svc.place_order(
        order_id="ORD-CHOREO-03",
        customer_id="CUST-CAROL",
        amount=3800.0,
        items=(("SKU-CONSOLE", 1),),
        shipping_postal_code="04538-133",
    )
    status3 = order_svc.get_order_status("ORD-CHOREO-03")
    print(f"Status Final do Pedido no OrderService: {status3}")
    print_event_timeline(broker, "ORD-CHOREO-03")
    assert status3 == "CANCELLED"

    # -------------------------------------------------------------------------
    # Cenário 4: Falha na Entrega (CEP Bloqueado) -> Compensações Reativas em Cadeia
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Falha de Logística gerando Reações em Cadeia (Estoque + Pagamento + Pedido)")
    stock_iphone_before = inventory_svc.get_stock("SKU-IPHONE")
    order_svc.place_order(
        order_id="ORD-CHOREO-04",
        customer_id="CUST-DANIEL",
        amount=5500.0,
        items=(("SKU-IPHONE", 1),),
        shipping_postal_code="99999-999",  # CEP bloqueado
    )
    status4 = order_svc.get_order_status("ORD-CHOREO-04")
    print(f"Status Final do Pedido no OrderService: {status4}")
    print_event_timeline(broker, "ORD-CHOREO-04")
    assert status4 == "CANCELLED"
    # Confere se o estoque foi restaurado pela reação ao evento
    assert inventory_svc.get_stock("SKU-IPHONE") == stock_iphone_before

    print_separator("Todos os cenários de Saga Coreografada foram validados com sucesso!")


if __name__ == "__main__":
    main()
