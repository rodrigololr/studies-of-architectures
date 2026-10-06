"""
exceptions.py - Exceções do domínio de checkout.
"""

from __future__ import annotations


class CheckoutDomainException(Exception):
    """Exceção base para o processo de fechamento de pedido."""
    pass


class EmptyCartException(CheckoutDomainException):
    """Lançada quando a lista de itens da compra está vazia."""
    pass


class InsufficientStockException(CheckoutDomainException):
    """Lançada quando a reserva de estoque é rejeitada pelo almoxarifado."""
    pass


class PaymentAuthorizationException(CheckoutDomainException):
    """Lançada quando o adquirente recusa a transação de pagamento."""
    pass


class InvalidShippingAddressException(CheckoutDomainException):
    """Lançada quando o CEP/endereço informado é inválido para cálculo de frete."""
    pass
