"""Implementação Interna do Módulo Notifications (Schema: notifications)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class _InternalNotification:
    notification_id: str
    recipient_id: str
    channel: str
    message: str
    sent_at: datetime = field(default_factory=datetime.now)


class _InternalNotificationRepository:
    def __init__(self) -> None:
        self._history: List[_InternalNotification] = []

    def save(self, notif: _InternalNotification) -> None:
        self._history.append(notif)

    def list_by_recipient(self, recipient_id: str) -> List[_InternalNotification]:
        return [n for n in self._history if n.recipient_id == recipient_id]

    def list_all(self) -> List[_InternalNotification]:
        return list(self._history)
