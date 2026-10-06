"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções ricas de domínio e regras de negócio.
"""


class BusinessException(Exception):
    """Classe base para erros de negócio."""
    pass


class InvalidOrderException(BusinessException):
    """Lançada quando os dados do pedido violam regras essenciais."""
    pass


class CouponExpiredException(BusinessException):
    """Lançada quando um cupom é inválido ou expirou."""
    pass


class OrderNotFoundException(BusinessException):
    """Lançada quando um pedido não é localizado."""
    pass
