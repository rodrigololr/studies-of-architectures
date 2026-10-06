"""
rest_api_adapter.py - Adaptador Primário HTTP REST para disparo de notificações.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
import uuid
from domain.models import (
    NotificationMessage,
    Recipient,
    NotificationPriority,
    ChannelType,
)
from domain.exceptions import NotificationDomainException
from ports.driver import SendNotificationUseCasePort


class NotificationRestController:
    def __init__(self, use_case: SendNotificationUseCasePort) -> None:
        self.use_case = use_case

    def handle_post_notify(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            recipient_data = payload.get("recipient", {})
            recipient = Recipient(
                user_id=recipient_data.get("user_id", str(uuid.uuid4())[:8]),
                name=recipient_data.get("name", "Usuário"),
                email=recipient_data.get("email", ""),
                phone_number=recipient_data.get("phone", ""),
            )

            priority_str = payload.get("priority", "MEDIUM")
            priority = NotificationPriority[priority_str]

            preferred = [
                ChannelType[ch] for ch in payload.get("preferred_channels", [])
                if ch in ChannelType.__members__
            ]

            message = NotificationMessage(
                message_id=str(uuid.uuid4())[:8],
                recipient=recipient,
                template_name=payload.get("template", ""),
                template_params=payload.get("params", {}),
                priority=priority,
                preferred_channels=preferred,
            )

            result = self.use_case.dispatch(message)

            return 200, {
                "success": True,
                "message_id": result.message_id,
                "channel_used": result.channel_used.value,
                "status": result.status.value,
                "rendered_text": result.content_rendered,
            }

        except NotificationDomainException as err:
            return 400, {
                "success": False,
                "error": err.__class__.__name__,
                "detail": str(err),
            }
        except Exception as ex:
            return 500, {
                "success": False,
                "error": "InternalServerError",
                "detail": str(ex),
            }
