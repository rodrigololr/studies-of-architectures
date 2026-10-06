"""Outbox Record Model and Status Enums."""

import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any


class OutboxStatus(Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


@dataclass
class OutboxRecord:
    event_id: str
    aggregate_type: str  # ex: "WALLET"
    aggregate_id: str    # ex: "WALLET-100"
    event_type: str      # ex: "FundsTransferred"
    payload: Dict[str, Any]
    status: OutboxStatus = OutboxStatus.PENDING
    created_at: float = field(default_factory=time.time)
    published_at: float = 0.0
    retry_count: int = 0
