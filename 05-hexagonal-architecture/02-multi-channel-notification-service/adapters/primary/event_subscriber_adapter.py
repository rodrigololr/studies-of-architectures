"""
event_subscriber_adapter.py - Adaptador Primário de Fila / Mensageria (ex: RabbitMQ/Kafka).

Simula um consumer assíncrono que escuta tópicos de eventos do sistema
(ex: 'user.security_alert') e aciona a Driver Port do hexágono.
"""

from __future__ import annotations
from typing import Dict, Any
import uuid
from domain.models import (
    NotificationMessage,
    Recipient,
    NotificationPriority,
    ChannelType,
)
from ports.driver import SendNotificationUseCasePort


class SecurityEventSubscriberAdapter:
    def __init__(self, use_case: SendNotificationUseCasePort) -> None:
        self.use_case = use_case

    def on_security_incident_event(self, event_payload: Dict[str, Any]) -> None:
        """Manipula um evento assíncrono recebido de um message broker."""
        print(f"\n[Event Consumer] Processando evento de tópico: {event_payload.get('event_type')}")

        user_info = event_payload.get("user", {})
        recipient = Recipient(
            user_id=user_info.get("id", "usr-auto"),
            name=user_info.get("name", "Membro"),
            email=user_info.get("email", ""),
            phone_number=user_info.get("phone", ""),
        )

        message = NotificationMessage(
            message_id=f"evt_{uuid.uuid4().hex[:6]}",
            recipient=recipient,
            template_name="security.alert",
            template_params={
                "ip_address": event_payload.get("ip_address", "0.0.0.0"),
                "location": event_payload.get("location", "Desconhecido"),
            },
            priority=NotificationPriority.CRITICAL_2FA,
            preferred_channels=[ChannelType.WHATSAPP, ChannelType.SMS, ChannelType.EMAIL],
        )

        result = self.use_case.dispatch(message)
        print(f"[Event Consumer] Notificação entregue via canal: {result.channel_used.value} (Status: {result.status.value})")
