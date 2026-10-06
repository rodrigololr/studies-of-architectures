"""Implementação Interna do Módulo Accounts (Schema: accounts)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
from modules.accounts.public_contracts import InsufficientFundsError


@dataclass
class _InternalAccount:
    account_id: str
    owner_name: str
    cpf: str
    pix_key: str
    balance: float = 0.0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def debit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Valor de débito deve ser estritamente positivo.")
        if self.balance < amount:
            raise InsufficientFundsError(
                f"Saldo insuficiente na conta '{self.account_id}'. Atual: R$ {self.balance:,.2f}, Débito: R$ {amount:,.2f}."
            )
        self.balance = round(self.balance - amount, 2)

    def credit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Valor de crédito deve ser estritamente positivo.")
        self.balance = round(self.balance + amount, 2)


class _InternalAccountsRepository:
    def __init__(self) -> None:
        self._accounts: Dict[str, _InternalAccount] = {}

    def save(self, acc: _InternalAccount) -> None:
        self._accounts[acc.account_id] = acc

    def find_by_id(self, account_id: str) -> Optional[_InternalAccount]:
        return self._accounts.get(account_id)

    def find_by_pix_key(self, pix_key: str) -> Optional[_InternalAccount]:
        for a in self._accounts.values():
            if a.pix_key.lower() == pix_key.lower():
                return a
        return None
