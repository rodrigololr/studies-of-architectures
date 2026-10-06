"""
entities/exceptions.py - Camada 1: Exceções de Regra de Negócio de Entidade.
"""

from __future__ import annotations


class EntityException(Exception):
    """Exceção base para regras de negócio das entidades."""
    pass


class InvalidPlanException(EntityException):
    """Lançada quando a configuração de um plano é inválida."""
    pass


class SubscriptionAlreadyCancelledException(EntityException):
    """Lançada quando se tenta alterar uma assinatura já cancelada."""
    pass
