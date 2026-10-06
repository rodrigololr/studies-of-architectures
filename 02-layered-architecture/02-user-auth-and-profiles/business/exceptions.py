"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções ricas para falhas de autenticação, permissão e regras de usuário.
"""


class BusinessException(Exception):
    pass


class UserAlreadyExistsException(BusinessException):
    pass


class InvalidCredentialsException(BusinessException):
    pass


class AccountDisabledException(BusinessException):
    pass


class UnauthorizedException(BusinessException):
    pass
