"""
pos_controller.py - Camada de Controlador (Controller).

Coordena a sequência de ações do operador de checkout:
- Abrir nova venda.
- Escanear produtos e notificar o display do caixa.
- Cancelar itens.
- Finalizar venda e comandar a emissão do cupom fiscal.
"""

from __future__ import annotations
from models.pos_model import PosModel, PaymentMethod
from views.pos_view import PosConsoleView


class PosController:
    def __init__(self, model: PosModel) -> None:
        self.model = model
        self.view = PosConsoleView()

    def open_checkout(self) -> None:
        self.model.start_new_sale()
        print("\n[PDV] Caixa Aberto. Pronto para passar produtos...")

    def scan(self, barcode: str, quantity: int = 1) -> None:
        item = self.model.scan_item(barcode, quantity)
        self.view.render_item_scanned(item, self.model.current_total)

    def cancel_last(self) -> None:
        item = self.model.cancel_last_item()
        if item:
            self.view.render_item_cancelled(item, self.model.current_total)
        else:
            print("  ⚠️ Nenhum item no carrinho para cancelar.")

    def checkout(self, payment_method: PaymentMethod, amount_paid: float) -> None:
        receipt = self.model.finalize_sale(payment_method, amount_paid)
        self.view.render_receipt(receipt)
