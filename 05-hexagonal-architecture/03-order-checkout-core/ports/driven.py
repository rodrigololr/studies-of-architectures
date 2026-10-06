"""
driven.py - Portas Secundárias / Outbound do núcleo de checkout.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import (
    OrderItem,
    CustomerInfo,
    PaymentConfirmation,
    InvoiceDetails,
    Order,
)


class InventoryReservationPort(ABC):
    @abstractmethod
    def reserve_stock(self, order_id: str, items: List[OrderItem]) -> bool:
        """Bloqueia unidades no estoque para o pedido."""
        pass

    @abstractmethod
    def release_stock(self, order_id: str, items: List[OrderItem]) -> None:
        """Compensa/libera unidades bloqueadas caso a cobrança falhe."""
        pass


class ShippingCalculatorPort(ABC):
    @abstractmethod
    def calculate_shipping(self, postal_code: str, items: List[OrderItem]) -> float:
        """Calcula a taxa de entrega baseada no CEP e cubagem dos produtos."""
        pass


class PaymentGatewayPort(ABC):
    @abstractmethod
    def charge(
        self,
        order_id: str,
        amount: float,
        customer: CustomerInfo,
        card_token: str,
    ) -> PaymentConfirmation:
        """Processa a captura financeira no adquirente."""
        pass


class FiscalInvoicePort(ABC):
    @abstractmethod
    def issue_invoice(self, order: Order) -> InvoiceDetails:
        """Transmite e autoriza a Nota Fiscal Eletrônica no órgão competente."""
        pass


class OrderRepositoryPort(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        """Persiste ou atualiza o pedido no banco de dados."""
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Recupera pedido pelo identificador primário."""
        pass
