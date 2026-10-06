"""
exceptions.py - Exceções do domínio de oráculo cripto.
"""

from __future__ import annotations


class OracleDomainException(Exception):
    """Exceção base para o oráculo de taxas de câmbio."""
    pass


class UnsupportedSymbolException(OracleDomainException):
    """Lançada quando o par de moedas solicitado não é suportado pelo motor."""
    pass


class OracleQuorumFailedException(OracleDomainException):
    """Lançada quando o número mínimo de fontes confiáveis (quórum) não foi alcançado."""
    pass
