"""
main.py - Demonstração executável do Pipeline de Checkout (Pipes and Filters).

Demonstra a esteira de validação pré-pagamento com interrupção precoce (short-circuiting):
- Pedido 1: Aprovado com sucesso com cálculo fiscal de ICMS.
- Pedido 2: Reprovado pelo filtro de Antifraude por uso de e-mail descartável.
- Pedido 3: Reprovado pelo filtro de Estoque por indisponibilidade de produto.
"""

from pipeline.base import OrderValidationPipeline
from pipeline.context import OrderCheckoutContext, CheckoutItem
from filters.schema_validation_filter import SchemaValidationFilter
from filters.fraud_risk_filter import FraudRiskFilter
from filters.inventory_check_filter import InventoryCheckFilter
from filters.fiscal_tax_filter import FiscalTaxFilter


def main() -> None:
    print("=" * 82)
    print("DEMONSTRAÇÃO: Pipes and Filters (Pipeline de Validação e Checkout de Pedidos)")
    print("=" * 82)

    # 1. Estoque do centro de distribuição
    inventory = {
        "prod-1": 15,  # Teclado Mecânico (15 un)
        "prod-2": 3,   # Mouse Gamer (3 un)
        "prod-3": 0,   # Monitor 4K (Esgotado!)
    }

    # 2. Montagem do Pipeline
    pipeline = OrderValidationPipeline()
    pipeline.add_filter(SchemaValidationFilter())
    pipeline.add_filter(FraudRiskFilter())
    pipeline.add_filter(InventoryCheckFilter(inventory))
    pipeline.add_filter(FiscalTaxFilter())

    # 3. Pedidos submetidos ao pipeline
    orders_to_process = [
        # Pedido 1: Pedido Legítimo
        OrderCheckoutContext(
            order_id="PED-1001",
            customer_id="cli-881",
            customer_email="marcelo.costa@empresa.com",
            destination_state="SP",
            items=[
                CheckoutItem("prod-1", "Teclado Mecânico", quantity=2, unit_price=250.0),
                CheckoutItem("prod-2", "Mouse Gamer", quantity=1, unit_price=180.0),
            ],
        ),
        # Pedido 2: Tentativa de Fraude (E-mail descartável)
        OrderCheckoutContext(
            order_id="PED-1002",
            customer_id="cli-992",
            customer_email="golpista@tempmail.com",
            destination_state="RJ",
            items=[
                CheckoutItem("prod-1", "Teclado Mecânico", quantity=1, unit_price=250.0),
            ],
        ),
        # Pedido 3: Produto Esgotado no Armazém
        OrderCheckoutContext(
            order_id="PED-1003",
            customer_id="cli-773",
            customer_email="fernanda@cliente.com",
            destination_state="MG",
            items=[
                CheckoutItem("prod-3", "Monitor 4K", quantity=1, unit_price=2800.0),
            ],
        ),
    ]

    print("\n--- Executando Validações na Esteira de Checkout ---")

    for order in orders_to_process:
        print(f"\n[SUBMISSÃO] Pedido: {order.order_id} | Cliente: {order.customer_id} ({order.customer_email})")
        result: OrderCheckoutContext = pipeline.execute(order)

        if result.is_approved:
            sub_f = f"R$ {result.subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tax_f = f"R$ {result.tax_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tot_f = f"R$ {result.final_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            print("  ✅ PEDIDO APROVADO PARA COBRANÇA:")
            print(f"     • Subtotal Itens:  {sub_f}")
            print(f"     • Imposto ({result.destination_state}):   {tax_f}")
            print(f"     • Total a Cobrar:  {tot_f}")
            print("     -> Pronto para envio ao Gateway de Pagamento.")
        else:
            print(f"  ❌ REPROVADO NO ESTÁGIO [{result.rejection_stage}]:")
            print(f"     Motivo: {result.rejection_reason}")

    print("\n" + "=" * 82)


if __name__ == "__main__":
    main()
