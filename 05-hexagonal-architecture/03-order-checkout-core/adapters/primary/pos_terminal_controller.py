"""
pos_terminal_controller.py - Adaptador Primário de Ponto de Venda Físico (PDV / POS).

Demonstra a versatilidade da Arquitetura Hexagonal: um terminal físico de caixa de loja
utiliza exatamente o mesmo núcleo de aplicação do e-commerce web.
"""

from __future__ import annotations
from domain.models import CheckoutCommand, CustomerInfo, OrderItem
from ports.driver import CheckoutUseCasePort


class PosTerminalController:
    def __init__(self, checkout_use_case: CheckoutUseCasePort, store_id: str) -> None:
        self.checkout_use_case = checkout_use_case
        self.store_id = store_id

    def process_store_sale(self, receipt_id: str, sku: str, name: str, price: float, qty: int) -> str:
        # Venda física tem frete local (CEP da loja) e cliente de balcão
        customer = CustomerInfo(
            customer_id="balcao-loja",
            name="Consumidor Final",
            email="loja@varejo.com",
            postal_code="01310-100",  # Av Paulista
        )
        item = OrderItem(sku=sku, name=name, unit_price=price, quantity=qty)
        cmd = CheckoutCommand(
            order_id=receipt_id,
            customer=customer,
            items=[item],
            card_token="tok_pos_chip_contactless",
        )
        res = self.checkout_use_case.execute_checkout(cmd)
        return f"[PDV Loja {self.store_id}] Venda {res.order_id} concluída! Total: R$ {res.grand_total:.2f} | NF-e: {res.invoice_number}"
