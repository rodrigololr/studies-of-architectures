"""
exceptions.py - Exceções de domínio da análise de crédito.
"""

from __future__ import annotations


class CreditDomainException(Exception):
    """Exceção base de domínio para esteira de crédito."""
    pass


class InvalidProposalException(CreditDomainException):
    """Lançada quando os parâmetros da proposta violam regras básicas de negócio."""
    pass


class BureauUnavailableException(CreditDomainException):
    """Lançada quando nenhum birô de crédito responde às consultas cadastrais."""
    pass
