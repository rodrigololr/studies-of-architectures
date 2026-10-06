"""
pos_model.py - Camada de Modelo (Model).

Modelos para catálogo de produtos por código de barras, carrinho de compras
ativo da frente de caixa e regras de cálculo de troco e pagamento.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import uuid


class PaymentMethod(str, Enum):
    CASH = "DINHEIRO"
    CREDIT_CARD = "CARTÃO DE CRÉDITO"
    DEBIT_CARD = "CARTÃO DE DÉBITO"
    PIX = "PIX"


@dataclass(frozen=True)
class Product:
    barcode: str
    description: str
    unit_price: float


@dataclass
class CartItem:
    item_number: int
    product: Product
    quantity: int

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.product.unit_price, 2)


@dataclass
class SaleReceipt:
    sale_id: str
    items: List[CartItem]
    total_amount: float
    payment_method: PaymentMethod
    amount_paid: float
    change_due: float


class PosModel:
    def __init__(self) -> None:
        # Catálogo pré-carregado de produtos no PDV
        self._catalog: Dict[str, Product] = {
            "78910001001": Product("78910001001", "Café Torrado e Moído 500g", 18.90),
            "78910001002": Product("78910001002", "Leite Integral UHT 1L", 5.40),
            "78910001003": Product("78910001003", "Pão Francês Tradicional 500g", 7.20),
            "78910001004": Product("78910001004", "Chocolate ao Leite 100g", 8.50),
        }
        self._current_cart: List[CartItem] = []
        self._is_sale_open: bool = False

    def start_new_sale(self) -> None:
        self._current_cart.clear()
        self._is_sale_open = True

    def scan_item(self, barcode: str, quantity: int = 1) -> CartItem:
        if not self._is_sale_open:
            raise RuntimeError("Nenhuma venda está aberta no PDV.")
        if quantity <= 0:
            raise ValueError("A quantidade deve ser positiva.")

        product = self._catalog.get(barcode)
        if not product:
            raise KeyError(f"Código de barras '{barcode}' não cadastrado no catálogo.")

        item_num = len(self._current_cart) + 1
        item = CartItem(item_number=item_num, product=product, quantity=quantity)
        self._current_cart.append(item)
        return item

    def cancel_last_item(self) -> Optional[CartItem]:
        if not self._current_cart:
            return None
        return self._current_cart.pop()

    @property
    def current_total(self) -> float:
        return round(sum(i.subtotal for i in self._current_cart), 2)

    def finalize_sale(self, payment_method: PaymentMethod, amount_paid: float) -> SaleReceipt:
        if not self._current_cart:
            raise RuntimeError("Não é possível fechar uma venda com o carrinho vazio.")

        total = self.current_total
        if amount_paid < total:
            raise ValueError(
                f"Valor pago insuficiente. Total: R$ {total:.2f}, Valor recebido: R$ {amount_paid:.2f}."
            )

        change = round(amount_paid - total, 2)
        receipt = SaleReceipt(
            sale_id=f"CFE-{str(uuid.uuid4())[:8].upper()}",
            items=list(self._current_cart),
            total_amount=total,
            payment_method=payment_method,
            amount_paid=round(amount_paid, 2),
            change_due=change,
        )

        self._is_sale_open = False
        self._current_cart.clear()
        return receipt
