"""
driver.py - Portas Primárias / Inbound do núcleo de checkout.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from domain.models import CheckoutCommand, CheckoutResult, Order


class CheckoutUseCasePort(ABC):
    @abstractmethod
    def execute_checkout(self, command: CheckoutCommand) -> CheckoutResult:
        """Orquestra as etapas de cálculo, reserva, cobrança, emissão fiscal e gravação."""
        pass


class GetOrderStatusUseCasePort(ABC):
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Consulta o estado atual do pedido processado."""
        pass
