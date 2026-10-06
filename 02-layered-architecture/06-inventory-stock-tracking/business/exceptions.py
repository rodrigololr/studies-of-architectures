"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções relacionadas a controle de armazém e saldo de estoque.
"""


class BusinessException(Exception):
    pass


class ProductNotFoundException(BusinessException):
    pass


class InsufficientStockException(BusinessException):
    pass


class InvalidStockOperationException(BusinessException):
    pass
