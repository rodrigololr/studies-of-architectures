"""
service.py - Camada de Negócio (Business Layer).

Responsável por orquestrar a lógica de negócio:
- Validar se o carrinho não está vazio.
- Calcular subtotais e regras de frete (Frete Grátis acima de R$ 200).
- Aplicar cupons válidos.
- Salvar na camada de dados via Repository.
"""

from __future__ import annotations
import uuid
from typing import List, Optional
from business.exceptions import InvalidOrderException, CouponExpiredException, OrderNotFoundException
from data.models import OrderModel, OrderItemModel, OrderStatus
from data.repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def create_order(
        self,
        customer_id: str,
        items_data: List[dict],
        coupon_code: Optional[str] = None,
    ) -> OrderModel:
        # 1. Regra de Negócio: Carrinho não pode ser vazio
        if not items_data:
            raise InvalidOrderException("O pedido precisa conter pelo menos um item.")

        items: List[OrderItemModel] = []
        for item in items_data:
            if item["quantity"] <= 0:
                raise InvalidOrderException(f"Quantidade do item '{item['product_name']}' deve ser maior que zero.")
            if item["unit_price"] <= 0:
                raise InvalidOrderException(f"Preço do item '{item['product_name']}' deve ser positivo.")

            items.append(
                OrderItemModel(
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )
            )

        # 2. Regra de Negócio: Cálculo de subtotal
        subtotal = sum(i.subtotal for i in items)

        # 3. Regra de Negócio: Frete (R$ 25 padrão; gratuito para pedidos a partir de R$ 200)
        freight = 0.0 if subtotal >= 200.0 else 25.0

        # 4. Regra de Negócio: Cupons de Desconto
        discount = 0.0
        if coupon_code:
            coupon_upper = coupon_code.upper().strip()
            if coupon_upper == "DESCONTO10":
                discount = round(subtotal * 0.10, 2)
            elif coupon_upper == "FRETEGRATIS":
                discount = freight
                freight = 0.0
            else:
                raise CouponExpiredException(f"Cupom '{coupon_code}' não existe ou está expirado.")

        total = round(max(0.0, (subtotal - discount) + freight), 2)

        # 5. Persistência na camada de dados
        order = OrderModel(
            order_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            items=items,
            freight_value=freight,
            discount_value=discount,
            total_amount=total,
            status=OrderStatus.PENDING_PAYMENT,
            coupon_code=coupon_code,
        )

        return self.repository.save(order)

    def mark_as_paid(self, order_id: str) -> OrderModel:
        order = self.repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Pedido com ID '{order_id}' não encontrado.")

        order.status = OrderStatus.PAID
        return self.repository.save(order)
