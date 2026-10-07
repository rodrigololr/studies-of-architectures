from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from domain.events import (
    DomainEvent,
    AccountOpened,
    FundsDeposited,
    FundsWithdrawn,
    FundsTransferredOut,
    FundsTransferredIn,
    AccountClosed,
)

@dataclass(frozen=True)
class StatementEntry:
    entry_id: str
    account_id: str
    timestamp: datetime
    operation: str
    amount: float
    running_balance: float
    description: str

class AccountStatementProjection:
    """
    Projeção desnormalizada de extrato bancário cronológico com saldo corrente acumulado.
    """

    def __init__(self):
        # Mapeamento: account_id -> lista cronológica de lançamentos de extrato
        self._statements: Dict[str, List[StatementEntry]] = {}
        # Rastreia saldo corrente em tempo de projeção para montar o running balance
        self._balances: Dict[str, float] = {}

    def handle(self, event: DomainEvent) -> None:
        acc_id = event.aggregate_id
        if acc_id not in self._statements:
            self._statements[acc_id] = []
            self._balances[acc_id] = 0.0

        current_balance = self._balances[acc_id]

        if isinstance(event, AccountOpened):
            current_balance = event.initial_balance
            self._balances[acc_id] = current_balance
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="ABERTURA",
                    amount=event.initial_balance,
                    running_balance=current_balance,
                    description=f"Abertura de conta em nome de {event.owner_name}",
                )
            )
        elif isinstance(event, FundsDeposited):
            current_balance += event.amount
            self._balances[acc_id] = current_balance
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="CRÉDITO",
                    amount=event.amount,
                    running_balance=current_balance,
                    description=event.description,
                )
            )
        elif isinstance(event, FundsWithdrawn):
            current_balance -= event.amount
            self._balances[acc_id] = current_balance
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="DÉBITO",
                    amount=-event.amount,
                    running_balance=current_balance,
                    description=event.description,
                )
            )
        elif isinstance(event, FundsTransferredOut):
            current_balance -= event.amount
            self._balances[acc_id] = current_balance
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="TRANSF_SAÍDA",
                    amount=-event.amount,
                    running_balance=current_balance,
                    description=f"Transferência enviada para conta {event.target_account_id} (Ref: {event.reference_id})",
                )
            )
        elif isinstance(event, FundsTransferredIn):
            current_balance += event.amount
            self._balances[acc_id] = current_balance
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="TRANSF_ENTRADA",
                    amount=event.amount,
                    running_balance=current_balance,
                    description=f"Transferência recebida de conta {event.source_account_id} (Ref: {event.reference_id})",
                )
            )
        elif isinstance(event, AccountClosed):
            self._statements[acc_id].append(
                StatementEntry(
                    entry_id=event.event_id,
                    account_id=acc_id,
                    timestamp=event.timestamp,
                    operation="ENCERRAMENTO",
                    amount=0.0,
                    running_balance=current_balance,
                    description=f"Conta encerrada: {event.reason}",
                )
            )

    def get_statement(self, account_id: str) -> List[StatementEntry]:
        return list(self._statements.get(account_id, []))
