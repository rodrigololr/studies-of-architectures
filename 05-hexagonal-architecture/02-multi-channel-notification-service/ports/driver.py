"""
driver.py - Portas Primárias / Inbound do serviço de notificações.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from domain.models import NotificationMessage, DispatchResult


class SendNotificationUseCasePort(ABC):
    @abstractmethod
    def dispatch(self, message: NotificationMessage) -> DispatchResult:
        """Processa a mensagem, renderiza o template e envia através dos canais prioritários."""
        pass
