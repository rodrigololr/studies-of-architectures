"""
pos_view.py - Camada de Visão (View).

Renderiza a interface do operador de caixa e o Cupom Fiscal emitido.
"""

from __future__ import annotations
from models.pos_model import CartItem, SaleReceipt


class PosConsoleView:
    @staticmethod
    def render_item_scanned(item: CartItem, running_total: float) -> None:
        sub_str = f"R$ {item.subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tot_str = f"R$ {running_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"  🛒 BIP! [Item {item.item_number}] {item.quantity}x {item.product.description} -> {sub_str} | Subtotal: {tot_str}")

    @staticmethod
    def render_item_cancelled(item: CartItem, running_total: float) -> None:
        tot_str = f"R$ {running_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"  ❌ ITEM CANCELADO: {item.product.description} | Novo Subtotal: {tot_str}")

    @staticmethod
    def render_receipt(receipt: SaleReceipt) -> None:
        print("\n" + "=" * 52)
        print("          SUPERMERCADO CENTRAL S/A")
        print("       CNPJ: 12.345.678/0001-90 - MATRIZ")
        print("=" * 52)
        print(f" Extrato Nº: {receipt.sale_id}")
        print(" CUPOM FISCAL ELETRÔNICO - SAT / NFC-e")
        print("-" * 52)
        print(f"{'#':<3} {'DESCRIÇÃO':<26} {'QTD':<4} {'VL.UN':<7} {'TOTAL'}")
        print("-" * 52)

        for item in receipt.items:
            p = item.product
            un_str = f"{p.unit_price:.2f}"
            tot_str = f"{item.subtotal:.2f}"
            desc = p.description[:25]
            print(f"{item.item_number:<3} {desc:<26} {item.quantity:<4} {un_str:<7} {tot_str}")

        print("-" * 52)
        tot_f = f"R$ {receipt.total_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pgo_f = f"R$ {receipt.amount_paid:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        trc_f = f"R$ {receipt.change_due:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        print(f" TOTAL A PAGAR:                      {tot_f:>15}")
        print(f" FORMA DE PAGAMENTO:                 {receipt.payment_method.value}")
        print(f" VALOR RECEBIDO:                     {pgo_f:>15}")
        print(f" TROCO:                              {trc_f:>15}")
        print("=" * 52)
        print("       OBRIGADO PELA PREFERÊNCIA! VOLTE SEMPRE!")
        print("=" * 52)
