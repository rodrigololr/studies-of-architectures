"""
correios_shipping_adapter.py - Adaptador Secundário de Cálculo de Frete.
"""

from __future__ import annotations
from typing import List
from domain.models import OrderItem
from domain.exceptions import InvalidShippingAddressException
from ports.driven import ShippingCalculatorPort


class CorreiosShippingAdapter(ShippingCalculatorPort):
    def calculate_shipping(self, postal_code: str, items: List[OrderItem]) -> float:
        clean_cep = postal_code.replace("-", "").strip()
        if len(clean_cep) != 8 or not clean_cep.isdigit():
            raise InvalidShippingAddressException(f"CEP inválido: '{postal_code}'")

        # Regra de negócio do frete simulado:
        # Se CEP começa com '0' (Grande SP), taxa fixa de R$ 15.00
        # Demais regiões, taxa base R$ 25.00 + R$ 5.00 por item
        total_qty = sum(item.quantity for item in items)
        if clean_cep.startswith("0"):
            return 15.00
        else:
            return round(25.00 + (total_qty * 5.00), 2)
