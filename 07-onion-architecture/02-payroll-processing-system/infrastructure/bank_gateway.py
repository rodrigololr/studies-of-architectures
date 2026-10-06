"""
infrastructure/bank_gateway.py - Camada 4: Infrastructure (Casca Externa).
"""

from __future__ import annotations
from typing import List, Tuple
from application.interfaces import IBankPayrollTransferGateway


class MockBankPayrollTransferGateway(IBankPayrollTransferGateway):
    def __init__(self) -> None:
        self.transfers_log: List[Tuple[str, str, float]] = []

    def dispatch_direct_deposits(self, deposits: List[Tuple[str, str, float]]) -> bool:
        for dep in deposits:
            self.transfers_log.append(dep)
        return True
