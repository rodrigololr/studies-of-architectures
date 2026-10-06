"""Contrato Público do Módulo Accounts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class InsufficientFundsError(Exception):
    """Lançada quando a conta não possui saldo para débito."""
    pass


@dataclass(frozen=True)
class AccountDto:
    account_id: str
    owner_name: str
    cpf: str
    pix_key: str
    balance: float
    is_active: bool


@dataclass(frozen=True)
class CreateAccountCommand:
    owner_name: str
    cpf: str
    pix_key: str
    initial_deposit: float = 0.0


@dataclass(frozen=True)
class DebitAccountCommand:
    account_id: str
    amount: float
    description: str


@dataclass(frozen=True)
class CreditAccountCommand:
    account_id: str
    amount: float
    description: str


class IAccountsModule(ABC):
    @abstractmethod
    def create_account(self, cmd: CreateAccountCommand) -> AccountDto:
        pass

    @abstractmethod
    def get_account(self, account_id: str) -> Optional[AccountDto]:
        pass

    @abstractmethod
    def get_by_pix_key(self, pix_key: str) -> Optional[AccountDto]:
        pass

    @abstractmethod
    def debit(self, cmd: DebitAccountCommand) -> AccountDto:
        pass

    @abstractmethod
    def credit(self, cmd: CreditAccountCommand) -> AccountDto:
        pass
