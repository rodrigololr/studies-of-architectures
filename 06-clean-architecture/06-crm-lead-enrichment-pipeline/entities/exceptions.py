"""
entities/exceptions.py - Camada 1: Exceções de CRM e Vendas.
"""

from __future__ import annotations


class CrmEntityException(Exception):
    pass


class InvalidCorporateEmailException(CrmEntityException):
    pass
