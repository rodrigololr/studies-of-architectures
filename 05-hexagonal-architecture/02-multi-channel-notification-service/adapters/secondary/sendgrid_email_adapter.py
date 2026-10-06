"""
sendgrid_email_adapter.py - Adaptador Secundário para envio via Email (SendGrid).
"""

from __future__ import annotations
from domain.models import ChannelType, Recipient
from ports.driven import NotificationChannelPort


class SendGridEmailAdapter(NotificationChannelPort):
    def __init__(self, api_key: str, healthy: bool = True) -> None:
        self._api_key = api_key
        self._healthy = healthy
        self.sent_messages: list[tuple[str, str]] = []

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.EMAIL

    def is_healthy(self) -> bool:
        return self._healthy

    def set_healthy(self, healthy: bool) -> None:
        self._healthy = healthy

    def send(self, recipient: Recipient, content: str) -> bool:
        if not self._healthy or not recipient.email:
            return False
        # Simula envio SMTP/API do SendGrid
        self.sent_messages.append((recipient.email, content))
        print(f"    [SendGrid Email] Para: {recipient.email} | Msg: \"{content}\"")
        return True
