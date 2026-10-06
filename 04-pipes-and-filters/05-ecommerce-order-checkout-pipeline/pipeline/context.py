"""
context.py - Contexto do Pedido transportado no pipeline de checkout.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CheckoutItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class OrderCheckoutContext:
    order_id: str
    customer_id: str
    customer_email: str
    destination_state: str  # UF (SP, RJ, MG, etc.)
    items: List[CheckoutItem]
    subtotal: float = 0.0
    tax_amount: float = 0.0
    final_total: float = 0.0
    risk_score: int = 0
    is_approved: bool = True
    rejection_stage: Optional[str] = None
    rejection_reason: Optional[str] = None
