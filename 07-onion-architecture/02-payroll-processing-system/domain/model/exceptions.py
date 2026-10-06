"""
domain/model/exceptions.py - Camada 1: Exceções de Domínio.
"""

from __future__ import annotations


class PayrollDomainException(Exception):
    pass


class InactiveEmployeeException(PayrollDomainException):
    pass
