"""
infrastructure/payment_gateway.py - Camada 4: Infrastructure (Casca Externa).
"""

from __future__ import annotations
from typing import List, Tuple
from application.interfaces import IPaymentSettlementGateway


class MockPaymentSettlementGateway(IPaymentSettlementGateway):
    def __init__(self) -> None:
        self.transactions: List[Tuple[str, float, str]] = []

    def process_charge(self, customer_name: str, amount: float, description: str) -> bool:
        self.transactions.append((customer_name, amount, description))
        return True
