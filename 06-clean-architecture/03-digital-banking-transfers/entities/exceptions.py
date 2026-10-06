"""
entities/exceptions.py - Camada 1: Exceções de Domínio Bancário.
"""

from __future__ import annotations


class BankingEntityException(Exception):
    pass


class InsufficientFundsException(BankingEntityException):
    pass


class AccountBlockedException(BankingEntityException):
    pass
