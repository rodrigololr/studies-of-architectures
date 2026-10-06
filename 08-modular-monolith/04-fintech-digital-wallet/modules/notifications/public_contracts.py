"""Contrato Público do Módulo Notifications."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class NotificationDto:
    notification_id: str
    recipient_id: str
    channel: str  # "PUSH", "SMS", "EMAIL"
    message: str
    sent_at: datetime


class INotificationsModule(ABC):
    @abstractmethod
    def list_notifications(self, recipient_id: str) -> List[NotificationDto]:
        pass

    @abstractmethod
    def list_all(self) -> List[NotificationDto]:
        pass
