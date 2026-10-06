"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções financeiras de saldo insuficiente e regras monetárias.
"""


class BusinessException(Exception):
    pass


class WalletNotFoundException(BusinessException):
    pass


class InsufficientFundsException(BusinessException):
    pass


class InvalidAmountException(BusinessException):
    pass
