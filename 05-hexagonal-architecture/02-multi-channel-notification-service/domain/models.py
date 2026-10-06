"""
models.py - Modelos de domínio do serviço de notificações.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any


class ChannelType(str, Enum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class NotificationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    CRITICAL_2FA = "CRITICAL_2FA"


class DispatchStatus(str, Enum):
    DELIVERED = "DELIVERED"
    FALLBACK_DELIVERED = "FALLBACK_DELIVERED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Recipient:
    user_id: str
    name: str
    email: str
    phone_number: str


@dataclass(frozen=True)
class NotificationMessage:
    message_id: str
    recipient: Recipient
    template_name: str
    template_params: Dict[str, Any]
    priority: NotificationPriority
    preferred_channels: list[ChannelType] = field(default_factory=list)


@dataclass(frozen=True)
class DispatchResult:
    message_id: str
    recipient_user_id: str
    channel_used: ChannelType
    status: DispatchStatus
    content_rendered: str
    dispatched_at: datetime
    error_details: Optional[str] = None
