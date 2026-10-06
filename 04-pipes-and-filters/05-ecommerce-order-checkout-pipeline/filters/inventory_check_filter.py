"""
inventory_check_filter.py - Filtro 3: Validação de Disponibilidade de Estoque.

Verifica se todos os itens do pedido estão disponíveis no inventário de armazém.
"""

from __future__ import annotations
from typing import Dict, Optional
from pipeline.base import Filter
from pipeline.context import OrderCheckoutContext


class InventoryCheckFilter(Filter[OrderCheckoutContext, OrderCheckoutContext]):
    def __init__(self, stock_inventory: Dict[str, int]) -> None:
        self.stock_inventory = stock_inventory

    def process(self, ctx: OrderCheckoutContext) -> Optional[OrderCheckoutContext]:
        if not ctx.is_approved:
            return ctx

        for item in ctx.items:
            available = self.stock_inventory.get(item.product_id, 0)
            if available < item.quantity:
                ctx.is_approved = False
                ctx.rejection_stage = "INVENTORY_CHECK"
                ctx.rejection_reason = (
                    f"Estoque insuficiente para o produto '{item.product_name}'. "
                    f"Disponível: {available}, Solicitado: {item.quantity}."
                )
                return ctx

        return ctx
