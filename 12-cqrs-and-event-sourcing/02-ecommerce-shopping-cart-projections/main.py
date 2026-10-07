import sys
from pathlib import Path

# Permite imports absolutos a partir da raiz do exemplo
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.event_store import AppendOnlyEventStore
from domain.commands import (
    CreateCartCommand,
    AddItemCommand,
    RemoveItemCommand,
    UpdateQuantityCommand,
    ApplyCouponCommand,
    CheckoutCartCommand,
    AbandonCartCommand,
)
from application.command_handlers import ShoppingCartCommandHandler
from projections.customer_live_cart import CustomerLiveCartProjection
from projections.abandoned_cart_analytics import AbandonedCartAnalyticsProjection

def main():
    print("=" * 80)
    print("EXEMPLO 02: CQRS & EVENT SOURCING - CARRINHO COM MÚLTIPLAS PROJEÇÕES")
    print("=" * 80)

    # 1. Instancia o Event Store Append-Only
    event_store = AppendOnlyEventStore()

    # 2. Instancia as duas projeções com propósitos radicalmente distintos
    live_cart_projection = CustomerLiveCartProjection()
    analytics_projection = AbandonedCartAnalyticsProjection()

    # 3. Assina os projetores no barramento do Event Store
    event_store.subscribe(live_cart_projection.handle)
    event_store.subscribe(analytics_projection.handle)

    # 4. Instancia o Command Handler
    handler = ShoppingCartCommandHandler(event_store)

    print("\n[FLUXO 1] Cliente Alice: Montagem de Carrinho, Cupom e Checkout")
    c1 = "CART-ALICE-101"
    handler.handle_create_cart(CreateCartCommand(cart_id=c1, customer_id="CUST-ALICE"))
    handler.handle_add_item(AddItemCommand(cart_id=c1, product_id="P-PHONE", product_name="Smartphone Pro 256GB", unit_price=3000.0, quantity=1))
    handler.handle_add_item(AddItemCommand(cart_id=c1, product_id="P-CASE", product_name="Capa Protetora Silicone", unit_price=100.0, quantity=1))
    handler.handle_apply_coupon(ApplyCouponCommand(cart_id=c1, coupon_code="BLACK10", discount_percentage=10.0))
    handler.handle_checkout(CheckoutCartCommand(cart_id=c1, payment_method="PIX"))
    print(f" -> Carrinho {c1} criado, preenchido com cupom 10% e finalizado com sucesso via PIX.")

    print("\n[FLUXO 2] Cliente Bob: Itens de Alto Valor e Abandono")
    c2 = "CART-BOB-202"
    handler.handle_create_cart(CreateCartCommand(cart_id=c2, customer_id="CUST-BOB"))
    handler.handle_add_item(AddItemCommand(cart_id=c2, product_id="P-LAPTOP", product_name="Notebook Gamer RTX", unit_price=7500.0, quantity=1))
    handler.handle_add_item(AddItemCommand(cart_id=c2, product_id="P-KEYBOARD", product_name="Teclado Mecânico RGB", unit_price=600.0, quantity=1))
    handler.handle_abandon(AbandonCartCommand(cart_id=c2, abandon_reason="PREÇO_ALTO"))
    print(f" -> Carrinho {c2} criado com Notebook e Teclado, e em seguida abandonado.")

    print("\n[FLUXO 3] Cliente Charlie: Modificações de Itens e Abandono")
    c3 = "CART-CHARLIE-303"
    handler.handle_create_cart(CreateCartCommand(cart_id=c3, customer_id="CUST-CHARLIE"))
    handler.handle_add_item(AddItemCommand(cart_id=c3, product_id="P-MONITOR", product_name="Monitor UltraWide 34'", unit_price=2200.0, quantity=1))
    handler.handle_add_item(AddItemCommand(cart_id=c3, product_id="P-CHAIR", product_name="Cadeira Ergonômica", unit_price=1800.0, quantity=1))
    handler.handle_remove_item(RemoveItemCommand(cart_id=c3, product_id="P-CHAIR"))
    handler.handle_update_quantity(UpdateQuantityCommand(cart_id=c3, product_id="P-MONITOR", new_quantity=2))
    handler.handle_abandon(AbandonCartCommand(cart_id=c3, abandon_reason="FRETE_CARO"))
    print(f" -> Carrinho {c3} teve itens alterados e foi abandonado por frete caro.")

    print("\n[FLUXO 4] Cliente Diana: Navegação Ativa (Carrinho Aberto)")
    c4 = "CART-DIANA-404"
    handler.handle_create_cart(CreateCartCommand(cart_id=c4, customer_id="CUST-DIANA"))
    handler.handle_add_item(AddItemCommand(cart_id=c4, product_id="P-EARBUDS", product_name="Fones Bluetooth TWS", unit_price=450.0, quantity=2))
    print(f" -> Carrinho {c4} criado e mantido ativo com 2 fones de ouvido.")

    print("\n" + "=" * 80)
    print("PROJEÇÃO 1: VISÃO DO COMPRADOR (CustomerLiveCartProjection)")
    print("=" * 80)

    alice_view = live_cart_projection.get_cart(c1)
    if alice_view:
        print(f"Recibo da Alice ({alice_view.cart_id}) - Status: [{alice_view.status}]:")
        for item in alice_view.items.values():
            print(f"  • {item.product_name:<30} | Qtd: {item.quantity:>2} | R$ {item.unit_price:>8.2f} un | Subtotal: R$ {item.total_price:>8.2f}")
        print(f"  Cupom: {alice_view.coupon_code} ({alice_view.discount_percentage}%) | Total Final Pago: R$ {alice_view.computed_total:.2f}")

    diana_view = live_cart_projection.get_cart(c4)
    if diana_view:
        print(f"\nCarrinho Ativo de Diana ({diana_view.cart_id}) - Status: [{diana_view.status}]:")
        for item in diana_view.items.values():
            print(f"  • {item.product_name:<30} | Qtd: {item.quantity:>2} | R$ {item.unit_price:>8.2f} un | Subtotal: R$ {item.total_price:>8.2f}")
        print(f"  Total Estimado: R$ {diana_view.computed_total:.2f}")

    print("\n" + "=" * 80)
    print("PROJEÇÃO 2: ANALYTICS DE MARKETING & GROWTH (AbandonedCartAnalyticsProjection)")
    print("=" * 80)

    summary = analytics_projection.get_dashboard_summary()
    print(f"Total de Carrinhos Criados:     {summary.total_carts_created}")
    print(f"Total de Checkouts Concluídos:  {summary.total_carts_checked_out}")
    print(f"Total de Carrinhos Abandonados: {summary.total_carts_abandoned}")
    print(f"Carrinhos Ativos em Sessão:     {summary.total_carts_active}")
    print(f"Taxa de Conversão de Checkout:  {summary.conversion_rate_percent}%")
    print(f"Receita Conquistada (Faturada): R$ {summary.total_recovered_revenue:>10.2f}")
    print(f"Receita Perdida em Abandonos:   R$ {summary.total_abandoned_revenue_loss:>10.2f}")

    print("\nRanking de Produtos Mais Abandonados (Perda Potencial em R$):")
    print(f"  {'Produto ID':<12} | {'Nome do Produto':<30} | {'Abandonos':<10} | {'Qtd':<5} | {'Perda Estimada (R$)'}")
    print("  " + "-" * 75)
    for stat in analytics_projection.get_top_abandoned_products():
        print(f"  {stat.product_id:<12} | {stat.product_name:<30} | {stat.abandon_occurrences:<10} | {stat.total_quantity_abandoned:<5} | R$ {stat.total_potential_loss:>12.2f}")

    print("\n[OK] Demonstração concluída com sucesso.")

if __name__ == "__main__":
    main()
