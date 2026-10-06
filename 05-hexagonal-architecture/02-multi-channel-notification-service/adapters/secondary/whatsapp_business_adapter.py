"""
whatsapp_business_adapter.py - Adaptador Secundário para envio via WhatsApp Cloud API.
"""

from __future__ import annotations
from domain.models import ChannelType, Recipient
from ports.driven import NotificationChannelPort


class WhatsAppBusinessAdapter(NotificationChannelPort):
    def __init__(self, phone_number_id: str, bearer_token: str, healthy: bool = True) -> None:
        self._phone_number_id = phone_number_id
        self._bearer_token = bearer_token
        self._healthy = healthy
        self.sent_messages: list[tuple[str, str]] = []

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.WHATSAPP

    def is_healthy(self) -> bool:
        return self._healthy

    def set_healthy(self, healthy: bool) -> None:
        self._healthy = healthy

    def send(self, recipient: Recipient, content: str) -> bool:
        if not self._healthy or not recipient.phone_number:
            return False
        # Simula envio via Meta WhatsApp Cloud API
        self.sent_messages.append((recipient.phone_number, content))
        print(f"    [WhatsApp Cloud API] Para: {recipient.phone_number} | Msg: \"{content}\"")
        return True
