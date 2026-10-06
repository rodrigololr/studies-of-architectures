"""
entities/exceptions.py - Camada 1: Exceções de Entidades.
"""

from __future__ import annotations


class EntityException(Exception):
    pass


class AuthorBannedException(EntityException):
    pass
