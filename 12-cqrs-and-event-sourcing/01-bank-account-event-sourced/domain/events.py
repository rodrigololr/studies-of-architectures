from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class AccountOpened(DomainEvent):
    owner_name: str = ""
    initial_balance: float = 0.0

@dataclass(frozen=True)
class FundsDeposited(DomainEvent):
    amount: float = 0.0
    description: str = ""

@dataclass(frozen=True)
class FundsWithdrawn(DomainEvent):
    amount: float = 0.0
    description: str = ""

@dataclass(frozen=True)
class FundsTransferredOut(DomainEvent):
    amount: float = 0.0
    target_account_id: str = ""
    reference_id: str = ""

@dataclass(frozen=True)
class FundsTransferredIn(DomainEvent):
    amount: float = 0.0
    source_account_id: str = ""
    reference_id: str = ""

@dataclass(frozen=True)
class AccountClosed(DomainEvent):
    reason: str = ""
