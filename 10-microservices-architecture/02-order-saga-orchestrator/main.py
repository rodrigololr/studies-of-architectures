"""Demonstração de Microsserviços: Transação Distribuída via Saga Orquestrada.

Cenários demonstrados:
1. Caminho Feliz: Pedido -> Pagamento -> Estoque -> Entrega -> Pedido Confirmado
2. Falha de Pagamento: Limite insuficiente -> Compensação cancela Pedido
3. Falha de Estoque: Produto esgotado -> Compensações estornam Pagamento e cancelam Pedido
4. Falha na Entrega: Região bloqueada -> Compensações em cascata (Devolve Estoque -> Estorna Pagamento -> Cancela Pedido)
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from saga.saga_models import (
    OrderItem,
    OrderDetails,
    OrderStatus,
    SagaStatus,
)
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.inventory_service import InventoryService
from services.delivery_service import DeliveryService
from saga.order_saga_orchestrator import OrderSagaOrchestrator


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Ecossistema de Microsserviços e Orquestrador de Saga...")

    # Instanciação dos 4 Microsserviços com seus bancos de dados isolados
    order_svc = OrderService()
    payment_svc = PaymentService()
    inventory_svc = InventoryService()
    delivery_svc = DeliveryService()

    # Orquestrador de Saga
    orchestrator = OrderSagaOrchestrator(
        order_svc=order_svc,
        payment_svc=payment_svc,
        inventory_svc=inventory_svc,
        delivery_svc=delivery_svc,
    )

    # -------------------------------------------------------------------------
    # Cenário 1: Caminho Feliz (Transação Distribuída 100% Concluída)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Compra Bem-Sucedida de iPhone 15 (Caminho Feliz)")
    order1 = OrderDetails(
        order_id="ORD-1001",
        customer_id="CUST-ALICE",
        items=[OrderItem(product_id="SKU-IPHONE-15", quantity=1, unit_price=6500.0)],
        total_amount=6500.0,
        shipping_postal_code="01310-100",
    )
    stock_before = inventory_svc.get_stock_level("SKU-IPHONE-15")
    res1 = orchestrator.execute_order_saga(order1)
    print(f"Status Final da Saga: {res1.final_status.value}")
    print("Histórico de Execução dos Microsserviços:")
    for step in res1.history:
        print(f"  [{step.action:<12}] {step.step.value:<18} -> {step.status}: {step.details}")
    assert res1.final_status == SagaStatus.SUCCESS
    assert order_svc.get_order_status("ORD-1001") == OrderStatus.CONFIRMED
    assert inventory_svc.get_stock_level("SKU-IPHONE-15") == stock_before - 1

    # -------------------------------------------------------------------------
    # Cenário 2: Falha no Pagamento (Limite de Crédito Excedido)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Falha de Pagamento (Cliente com Crédito Insuficiente)")
    order2 = OrderDetails(
        order_id="ORD-1002",
        customer_id="CUST-BOB",
        items=[OrderItem(product_id="SKU-IPHONE-15", quantity=1, unit_price=6500.0)],
        total_amount=6500.0,
        shipping_postal_code="01310-100",
    )
    res2 = orchestrator.execute_order_saga(order2)
    print(f"Status Final da Saga: {res2.final_status.value}")
    print(f"Motivo da Falha: {res2.failure_reason}")
    print("Histórico de Execução e Compensação:")
    for step in res2.history:
        print(f"  [{step.action:<12}] {step.step.value:<18} -> {step.status}: {step.details}")
    assert res2.final_status == SagaStatus.COMPENSATED
    assert order_svc.get_order_status("ORD-1002") == OrderStatus.CANCELLED

    # -------------------------------------------------------------------------
    # Cenário 3: Falha no Estoque (Produto Sem Saldo)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Falha no Estoque de PS5 Pro (Estorno de Pagamento + Cancelamento)")
    order3 = OrderDetails(
        order_id="ORD-1003",
        customer_id="CUST-CAROL",
        items=[OrderItem(product_id="SKU-PS5-PRO", quantity=1, unit_price=4500.0)],
        total_amount=4500.0,
        shipping_postal_code="01310-100",
    )
    res3 = orchestrator.execute_order_saga(order3)
    print(f"Status Final da Saga: {res3.final_status.value}")
    print(f"Motivo da Falha: {res3.failure_reason}")
    print("Histórico de Execução e Compensação:")
    for step in res3.history:
        print(f"  [{step.action:<12}] {step.step.value:<18} -> {step.status}: {step.details}")
    assert res3.final_status == SagaStatus.COMPENSATED
    assert order_svc.get_order_status("ORD-1003") == OrderStatus.CANCELLED
    # Confere que o pagamento foi estornado no histórico
    assert any(h.step.value == "PROCESS_PAYMENT" and h.action == "COMPENSATION" for h in res3.history)

    # -------------------------------------------------------------------------
    # Cenário 4: Falha na Entrega (Região com Restrição de Despacho)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Falha na Entrega (Compensação em Cascata: Estoque -> Pagamento -> Pedido)")
    stock_macbook_before = inventory_svc.get_stock_level("SKU-MACBOOK-AIR")
    order4 = OrderDetails(
        order_id="ORD-1004",
        customer_id="CUST-DANIEL",
        items=[OrderItem(product_id="SKU-MACBOOK-AIR", quantity=1, unit_price=8000.0)],
        total_amount=8000.0,
        shipping_postal_code="99999-999",  # CEP bloqueado
    )
    res4 = orchestrator.execute_order_saga(order4)
    print(f"Status Final da Saga: {res4.final_status.value}")
    print(f"Motivo da Falha: {res4.failure_reason}")
    print("Histórico de Execução e Compensações Reversas:")
    for step in res4.history:
        print(f"  [{step.action:<12}] {step.step.value:<18} -> {step.status}: {step.details}")
    assert res4.final_status == SagaStatus.COMPENSATED
    assert order_svc.get_order_status("ORD-1004") == OrderStatus.CANCELLED
    # Confere que tanto o estoque foi liberado quanto o pagamento estornado
    assert any(h.step.value == "RESERVE_INVENTORY" and h.action == "COMPENSATION" for h in res4.history)
    assert any(h.step.value == "PROCESS_PAYMENT" and h.action == "COMPENSATION" for h in res4.history)
    assert inventory_svc.get_stock_level("SKU-MACBOOK-AIR") == stock_macbook_before

    print_separator("Todos os cenários do Orquestrador de Saga foram validados com sucesso!")


if __name__ == "__main__":
    main()
