"""
exceptions.py - Exceções do domínio de notificações.
"""

from __future__ import annotations


class NotificationDomainException(Exception):
    """Exceção base de domínio para o serviço de mensageria."""
    pass


class InvalidRecipientException(NotificationDomainException):
    """Lançada quando os contatos do destinatário são inválidos."""
    pass


class TemplateNotFoundException(NotificationDomainException):
    """Lançada quando o template de mensagem solicitado não existe."""
    pass


class AllChannelsExhaustedException(NotificationDomainException):
    """Lançada quando todos os canais configurados e seus fallbacks falharam."""
    pass
