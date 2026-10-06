"""
main.py - Demonstração executável de Frente de Caixa (PDV de Varejo em MVC).

Simula a abertura de caixa, bip de itens com leitor de código de barras,
cancelamento de item, cálculo de troco e impressão do Cupom Fiscal.
"""

from models.pos_model import PosModel, PaymentMethod
from controllers.pos_controller import PosController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Arquitetura MVC (Frente de Caixa - PDV de Supermercado)")
    print("=" * 65)

    # 1. Instanciação do MVC
    model = PosModel()
    controller = PosController(model)

    # 2. Operador abre nova venda
    controller.open_checkout()

    # 3. Operador bipa produtos
    print("\n--- Passando Produtos na Esteira do Caixa ---")
    controller.scan("78910001001", quantity=1)  # Café 500g: R$ 18.90
    controller.scan("78910001002", quantity=2)  # Leite 1L (2x): R$ 10.80
    controller.scan("78910001003", quantity=1)  # Pão 500g: R$ 7.20
    controller.scan("78910001004", quantity=1)  # Chocolate 100g: R$ 8.50

    # 4. Cliente desiste do chocolate -> Operador cancela o último item
    print("\n--- Cliente Desistiu do Chocolate (Cancelamento de Item) ---")
    controller.cancel_last()

    # 5. Pagamento em dinheiro: Total da compra é R$ 36.90. Cliente entrega cédula de R$ 50.00
    print("\n--- Fechamento de Venda em Dinheiro com Cálculo de Troco ---")
    controller.checkout(payment_method=PaymentMethod.CASH, amount_paid=50.0)


if __name__ == "__main__":
    main()
