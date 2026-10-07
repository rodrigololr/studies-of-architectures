from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from domain.events import (
    DomainEvent,
    AccountOpened,
    FundsDeposited,
    FundsWithdrawn,
    FundsTransferredOut,
    FundsTransferredIn,
    AccountClosed,
)

@dataclass
class AccountSummaryView:
    account_id: str
    owner_name: str
    balance: float
    is_active: bool
    is_closed: bool
    version: int
    last_updated: datetime

class AccountSummaryProjection:
    """
    Projeção desnormalizada de resumo de contas.
    Otimizada para consultas O(1) de saldo e dados cadastrais.
    """

    def __init__(self):
        self._views: Dict[str, AccountSummaryView] = {}

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, AccountOpened):
            self._views[event.aggregate_id] = AccountSummaryView(
                account_id=event.aggregate_id,
                owner_name=event.owner_name,
                balance=event.initial_balance,
                is_active=True,
                is_closed=False,
                version=event.version,
                last_updated=event.timestamp,
            )
        elif isinstance(event, FundsDeposited):
            view = self._views[event.aggregate_id]
            view.balance += event.amount
            view.version = event.version
            view.last_updated = event.timestamp
        elif isinstance(event, FundsWithdrawn):
            view = self._views[event.aggregate_id]
            view.balance -= event.amount
            view.version = event.version
            view.last_updated = event.timestamp
        elif isinstance(event, FundsTransferredOut):
            view = self._views[event.aggregate_id]
            view.balance -= event.amount
            view.version = event.version
            view.last_updated = event.timestamp
        elif isinstance(event, FundsTransferredIn):
            view = self._views[event.aggregate_id]
            view.balance += event.amount
            view.version = event.version
            view.last_updated = event.timestamp
        elif isinstance(event, AccountClosed):
            view = self._views[event.aggregate_id]
            view.is_active = False
            view.is_closed = True
            view.version = event.version
            view.last_updated = event.timestamp

    def get_by_id(self, account_id: str) -> Optional[AccountSummaryView]:
        return self._views.get(account_id)

    def get_all(self) -> List[AccountSummaryView]:
        return list(self._views.values())
