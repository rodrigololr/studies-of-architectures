"""
exceptions.py - Exceções do domínio de armazenamento de documentos.
"""

from __future__ import annotations


class StorageDomainException(Exception):
    """Exceção base para o subsistema de armazenamento."""
    pass


class FileTooLargeException(StorageDomainException):
    """Lançada quando o arquivo excede o limite máximo configurado."""
    pass


class DisallowedFileTypeException(StorageDomainException):
    """Lançada quando a extensão ou MIME-type do arquivo é proibida por segurança."""
    pass


class MalwareDetectedException(StorageDomainException):
    """Lançada quando a inspeção antivírus identifica ameaça de segurança."""
    pass


class DocumentNotFoundException(StorageDomainException):
    """Lançada ao tentar baixar documento com identificador inexistente."""
    pass
