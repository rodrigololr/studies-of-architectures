"""
main.py - Composition Root e Demonstração do Exemplo 03.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.service import OrderCheckoutService
from adapters.secondary.warehouse_inventory_adapter import WarehouseInventoryAdapter
from adapters.secondary.correios_shipping_adapter import CorreiosShippingAdapter
from adapters.secondary.acquirer_payment_adapter import CieloPaymentAdapter
from adapters.secondary.sefaz_nfe_adapter import SefazNfeAdapter
from adapters.secondary.sql_order_repository_adapter import InMemoryOrderRepositoryAdapter
from adapters.primary.web_checkout_controller import WebCheckoutController
from adapters.primary.pos_terminal_controller import PosTerminalController


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 03: ORDER CHECKOUT CORE")
    print("=" * 80)

    # 1. Adaptadores Secundários (Driven)
    inventory_adapter = WarehouseInventoryAdapter(initial_stock={
        "SKU-MACBOOK": 3,
        "SKU-MOUSE": 5,
    })
    shipping_adapter = CorreiosShippingAdapter()
    payment_adapter = CieloPaymentAdapter()
    invoice_adapter = SefazNfeAdapter(cnpj_emissor="12345678000199")
    order_repo = InMemoryOrderRepositoryAdapter()

    # 2. Núcleo da Aplicação (Core / Hexágono)
    checkout_service = OrderCheckoutService(
        inventory_port=inventory_adapter,
        shipping_port=shipping_adapter,
        payment_port=payment_adapter,
        invoice_port=invoice_adapter,
        order_repo=order_repo,
    )

    # 3. Adaptadores Primários (Driver)
    web_controller = WebCheckoutController(
        checkout_use_case=checkout_service,
        order_status_use_case=checkout_service,
    )
    pos_controller = PosTerminalController(
        checkout_use_case=checkout_service,
        store_id="SHOPPING-MORUMBI",
    )

    print("\n--- CENÁRIO 1: Checkout Web com Sucesso (Itens + Frete + Estoque + NF-e) ---")
    status, res = web_controller.handle_post_checkout({
        "order_id": "ORD-WEB-001",
        "customer": {
            "id": "cust-55",
            "name": "Beatriz Mendonça",
            "email": "beatriz@tech.com",
            "postal_code": "04571-010",
        },
        "items": [
            {"sku": "SKU-MACBOOK", "name": "MacBook Pro M3", "unit_price": 14000.0, "quantity": 1},
            {"sku": "SKU-MOUSE", "name": "Magic Mouse", "unit_price": 800.0, "quantity": 1},
        ],
        "card_token": "tok_valid_visa_approved",
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(f"Estoque restante -> MacBook: {inventory_adapter.get_available('SKU-MACBOOK')} | Mouse: {inventory_adapter.get_available('SKU-MOUSE')}")

    print("\n--- CENÁRIO 2: Pagamento Recusado -> Transação de Compensação (Rollback de Estoque) ---")
    print(f"Estoque ANTES da tentativa -> MacBook: {inventory_adapter.get_available('SKU-MACBOOK')}")
    status, res = web_controller.handle_post_checkout({
        "order_id": "ORD-WEB-002",
        "customer": {
            "id": "cust-88",
            "name": "Marcos Silva",
            "email": "marcos@fail.com",
            "postal_code": "04571-010",
        },
        "items": [
            {"sku": "SKU-MACBOOK", "name": "MacBook Pro M3", "unit_price": 14000.0, "quantity": 1},
        ],
        "card_token": "tok_declined_insufficient_funds",
    })
    print(f"Status HTTP: {status} | Resposta: {res}")
    print(f"Estoque DEPOIS da compensação -> MacBook: {inventory_adapter.get_available('SKU-MACBOOK')} (Preservado!)")

    print("\n--- CENÁRIO 3: Rejeição por Falta de Estoque ---")
    status, res = web_controller.handle_post_checkout({
        "order_id": "ORD-WEB-003",
        "customer": {
            "id": "cust-99",
            "name": "Comprador Agressivo",
            "email": "agressivo@loja.com",
            "postal_code": "01310-100",
        },
        "items": [
            {"sku": "SKU-MACBOOK", "name": "MacBook Pro M3", "unit_price": 14000.0, "quantity": 10},
        ],
        "card_token": "tok_valid_visa_approved",
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 4: Ponto de Venda Físico (PDV) Acionando o Mesmo Hexágono ---")
    pos_output = pos_controller.process_store_sale(
        receipt_id="ORD-POS-808",
        sku="SKU-MOUSE",
        name="Magic Mouse",
        price=800.0,
        qty=2,
    )
    print(pos_output)
    print(f"Estoque final de Mouse: {inventory_adapter.get_available('SKU-MOUSE')}")

    print("\n--- CENÁRIO 5: Consulta de Pedido no Repositório via Driver Port ---")
    order = checkout_service.get_order("ORD-WEB-001")
    if order:
        print(f"Pedido #{order.order_id} recuperado:")
        print(f" -> Status: {order.status.value}")
        print(f" -> Total Geral: R$ {order.grand_total:.2f} (Itens: R$ {order.items_total:.2f} + Frete: R$ {order.shipping_fee:.2f})")
        print(f" -> NF-e: {order.invoice_info.invoice_number if order.invoice_info else 'N/A'}")

    print("\n" + "=" * 80)
    print(" Exemplo 03 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
