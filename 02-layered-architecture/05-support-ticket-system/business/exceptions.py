"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções de regras de tickets e máquina de estados de suporte.
"""


class BusinessException(Exception):
    pass


class TicketNotFoundException(BusinessException):
    pass


class InvalidStatusTransitionException(BusinessException):
    pass


class TicketClosedException(BusinessException):
    pass
