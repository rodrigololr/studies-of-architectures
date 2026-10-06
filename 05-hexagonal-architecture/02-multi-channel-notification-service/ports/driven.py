"""
driven.py - Portas Secundárias / Outbound do serviço de notificações.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.models import ChannelType, Recipient, DispatchResult


class NotificationChannelPort(ABC):
    @property
    @abstractmethod
    def channel_type(self) -> ChannelType:
        """Tipo do canal suportado por esta porta."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Verifica se o provedor do canal está operacional."""
        pass

    @abstractmethod
    def send(self, recipient: Recipient, content: str) -> bool:
        """Envia o conteúdo para o destinatário. Retorna True se entregue."""
        pass


class TemplateEnginePort(ABC):
    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renderiza um template com as variáveis informadas."""
        pass


class NotificationHistoryRepositoryPort(ABC):
    @abstractmethod
    def record_dispatch(self, result: DispatchResult) -> None:
        """Persiste o log auditável do envio de notificação."""
        pass

    @abstractmethod
    def get_history(self) -> List[DispatchResult]:
        """Consulta todos os envios realizados."""
        pass
