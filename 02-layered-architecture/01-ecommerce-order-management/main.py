"""
main.py - Demonstração executável do fluxo em camadas (Order Management).

Instancia as camadas de baixo para cima (Repository -> Service -> Controller),
simula chamadas de requisição HTTP e exibe as respostas formatadas.
"""

from data.repository import OrderRepository
from business.service import OrderService
from presentation.controller import OrderController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Arquitetura em Camadas (Gestão de Pedidos E-commerce)")
    print("=" * 65)

    # Injeção de dependência top-down das camadas
    repository = OrderRepository()        # 1. Data Layer
    service = OrderService(repository)    # 2. Business Layer
    controller = OrderController(service) # 3. Presentation Layer

    # Caso 1: Pedido com frete padrão e cupom válido
    req_1 = {
        "customer_id": "cli-101",
        "coupon_code": "DESCONTO10",
        "items": [
            {"product_id": "p1", "product_name": "Teclado Mecânico", "quantity": 1, "unit_price": 150.0},
        ],
    }
    print("\n[REQUISIÇÃO 1] POST /api/orders/checkout (Total < R$ 200, Cupom 10%)")
    res_1 = controller.checkout(req_1)
    print(f"  HTTP {res_1['status_code']}: {res_1['data']}")

    order_id = res_1["data"]["order_id"]

    # Caso 2: Pagamento do pedido criado
    print(f"\n[REQUISIÇÃO 2] PATCH /api/orders/{order_id}/pay")
    res_2 = controller.pay_order(order_id)
    print(f"  HTTP {res_2['status_code']}: {res_2['data']}")

    # Caso 3: Pedido com valor alto (> R$ 200 ganha frete grátis)
    req_3 = {
        "customer_id": "cli-202",
        "items": [
            {"product_id": "p2", "product_name": "Monitor UltraWide", "quantity": 1, "unit_price": 1200.0},
        ],
    }
    print("\n[REQUISIÇÃO 3] POST /api/orders/checkout (Subtotal > R$ 200 -> Frete Grátis)")
    res_3 = controller.checkout(req_3)
    print(f"  HTTP {res_3['status_code']}: {res_3['data']}")

    # Caso 4: Validação de erro de negócio (carrinho vazio)
    req_4 = {"customer_id": "cli-303", "items": []}
    print("\n[REQUISIÇÃO 4] POST /api/orders/checkout (Carrinho Vazio -> Erro 400)")
    res_4 = controller.checkout(req_4)
    print(f"  HTTP {res_4['status_code']}: Erro = '{res_4['error']}'")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
