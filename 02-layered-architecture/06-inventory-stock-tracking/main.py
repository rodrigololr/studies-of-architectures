"""
main.py - Demonstração executável de Controle de Estoque e Armazém em Camadas.

Demonstra cadastro com saldo inicial, reserva para pedido, despacho físico,
disparo do alerta de ponto de reposição crítica e bloqueio por estoque insuficiente.
"""

from data.repository import InventoryRepository, StockMovementRepository
from business.service import InventoryService
from presentation.controller import InventoryController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Controle de Estoque e Armazém em Camadas")
    print("=" * 65)

    inv_repo = InventoryRepository()
    mov_repo = StockMovementRepository()
    service = InventoryService(inv_repo, mov_repo)
    controller = InventoryController(service)

    # 1. Cadastro de produto com estoque inicial de 20 un e alerta em 10 un
    print("\n[PASSO 1] POST /api/inventory/products (Cadastrando Memória RAM 16GB)...")
    prod_req = {
        "sku": "RAM-DDR5-16GB",
        "name": "Memória RAM Kingston Fury DDR5 16GB",
        "initial_qty": 20,
        "reorder_point": 10,  # Se o estoque físico for <= 10, dispara alerta
    }
    prod_res = controller.register_product(prod_req)
    print(f"  HTTP {prod_res['status_code']}: {prod_res['data']}")
    prod_id = prod_res["data"]["product_id"]

    # 2. Reserva de 6 unidades para um pedido em checkout
    print(f"\n[PASSO 2] POST /api/inventory/products/{prod_id}/reserve (Reservando 6 un)...")
    reserve_res = controller.reserve(prod_id, {"quantity": 6, "order_id": "ORD-5541"})
    print(f"  HTTP {reserve_res['status_code']}: {reserve_res['data']}")

    # 3. Tentativa de reservar mais do que o disponível (Restam 14 livres, pede 18)
    print(f"\n[PASSO 3] POST /api/inventory/products/{prod_id}/reserve (Tentando reservar 18 un)...")
    insufficient_res = controller.reserve(prod_id, {"quantity": 18, "order_id": "ORD-9999"})
    print(f"  HTTP {insufficient_res['status_code']} Unprocessable Entity: Erro = '{insufficient_res['error']}'")

    # 4. Despacho/Expedição das 6 unidades reservadas
    print(f"\n[PASSO 4] POST /api/inventory/products/{prod_id}/dispatch (Expedindo 6 un reservadas)...")
    dispatch_res = controller.dispatch(prod_id, {"quantity": 6, "order_id": "ORD-5541"})
    print(f"  HTTP {dispatch_res['status_code']}: {dispatch_res['data']}")

    # 5. Mais uma reserva e despacho que leva o estoque total para 9 un (abaixo de 10)
    print(f"\n[PASSO 5] Reservando e expedindo 5 unidades adicionais (levando total para 9 un)...")
    controller.reserve(prod_id, {"quantity": 5, "order_id": "ORD-8812"})
    dispatch_critico = controller.dispatch(prod_id, {"quantity": 5, "order_id": "ORD-8812"})
    dados_finais = dispatch_critico["data"]
    print(f"  Estoque Físico Restante: {dados_finais['total_physical']} un")
    print(f"  🚨 Alerta de Reposição Crítica Acionado: {dados_finais['reorder_alert']}")
    if dados_finais["reorder_alert"]:
        print("  ⚠️ Setor de Compras notificado: Estoque atingiu ou caiu abaixo do ponto de reposição!")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
