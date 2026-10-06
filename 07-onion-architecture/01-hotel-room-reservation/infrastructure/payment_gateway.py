"""
infrastructure/payment_gateway.py - Camada 4: Infrastructure (Casca Externa).
"""

from __future__ import annotations
from application.interfaces import IPaymentService


class MockStripePaymentService(IPaymentService):
    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed
        self.charges: list[tuple[str, float, str]] = []
        self.refunds: list[tuple[str, float]] = []

    def process_charge(self, guest_id: str, amount: float, description: str) -> bool:
        if not self.should_succeed or guest_id == "guest_declined":
            return False
        self.charges.append((guest_id, amount, description))
        return True

    def process_refund(self, guest_id: str, amount: float) -> bool:
        self.refunds.append((guest_id, amount))
        return True
