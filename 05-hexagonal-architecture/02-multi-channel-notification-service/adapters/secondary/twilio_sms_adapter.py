"""
twilio_sms_adapter.py - Adaptador Secundário para envio via SMS (Twilio).
"""

from __future__ import annotations
from domain.models import ChannelType, Recipient
from ports.driven import NotificationChannelPort


class TwilioSmsAdapter(NotificationChannelPort):
    def __init__(self, account_sid: str, auth_token: str, healthy: bool = True) -> None:
        self._sid = account_sid
        self._auth = auth_token
        self._healthy = healthy
        self.sent_messages: list[tuple[str, str]] = []

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.SMS

    def is_healthy(self) -> bool:
        return self._healthy

    def set_healthy(self, healthy: bool) -> None:
        self._healthy = healthy

    def send(self, recipient: Recipient, content: str) -> bool:
        if not self._healthy or not recipient.phone_number:
            return False
        # Simula despacho via Twilio SMS REST API
        self.sent_messages.append((recipient.phone_number, content))
        print(f"    [Twilio SMS] Para: {recipient.phone_number} | Msg: \"{content}\"")
        return True
