"""
schema_validation_filter.py - Filtro 1: Validação de Estrutura do Pedido.

Verifica se o cliente, e-mail e itens do carrinho são válidos e consistentes.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import OrderCheckoutContext


class SchemaValidationFilter(Filter[OrderCheckoutContext, OrderCheckoutContext]):
    def process(self, ctx: OrderCheckoutContext) -> Optional[OrderCheckoutContext]:
        if not ctx.customer_id.strip():
            ctx.is_approved = False
            ctx.rejection_stage = "SCHEMA_VALIDATION"
            ctx.rejection_reason = "Identificador do cliente é obrigatório."
            return ctx

        if not ctx.items:
            ctx.is_approved = False
            ctx.rejection_stage = "SCHEMA_VALIDATION"
            ctx.rejection_reason = "O pedido não pode ser submetido com carrinho vazio."
            return ctx

        for item in ctx.items:
            if item.quantity <= 0 or item.unit_price <= 0:
                ctx.is_approved = False
                ctx.rejection_stage = "SCHEMA_VALIDATION"
                ctx.rejection_reason = f"Item '{item.product_name}' contém quantidade ou preço inválido."
                return ctx

        ctx.subtotal = round(sum(i.subtotal for i in ctx.items), 2)
        return ctx
