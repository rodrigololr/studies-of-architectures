"""Ponto de Entrada e Facade do Módulo Accounts."""

import uuid
from typing import Optional
from modules.accounts.public_contracts import (
    IAccountsModule,
    AccountDto,
    CreateAccountCommand,
    DebitAccountCommand,
    CreditAccountCommand,
)
from modules.accounts.internal.accounts_internal import (
    _InternalAccount,
    _InternalAccountsRepository,
)


class AccountsModule(IAccountsModule):
    def __init__(self) -> None:
        self._repo = _InternalAccountsRepository()

    def create_account(self, cmd: CreateAccountCommand) -> AccountDto:
        acc_id = f"ACC_{uuid.uuid4().hex[:8].upper()}"
        acc = _InternalAccount(
            account_id=acc_id,
            owner_name=cmd.owner_name,
            cpf=cmd.cpf,
            pix_key=cmd.pix_key,
            balance=round(cmd.initial_deposit, 2),
        )
        self._repo.save(acc)
        return AccountDto(
            account_id=acc.account_id,
            owner_name=acc.owner_name,
            cpf=acc.cpf,
            pix_key=acc.pix_key,
            balance=acc.balance,
            is_active=acc.is_active,
        )

    def get_account(self, account_id: str) -> Optional[AccountDto]:
        acc = self._repo.find_by_id(account_id)
        if not acc:
            return None
        return AccountDto(
            account_id=acc.account_id,
            owner_name=acc.owner_name,
            cpf=acc.cpf,
            pix_key=acc.pix_key,
            balance=acc.balance,
            is_active=acc.is_active,
        )

    def get_by_pix_key(self, pix_key: str) -> Optional[AccountDto]:
        acc = self._repo.find_by_pix_key(pix_key)
        if not acc:
            return None
        return AccountDto(
            account_id=acc.account_id,
            owner_name=acc.owner_name,
            cpf=acc.cpf,
            pix_key=acc.pix_key,
            balance=acc.balance,
            is_active=acc.is_active,
        )

    def debit(self, cmd: DebitAccountCommand) -> AccountDto:
        acc = self._repo.find_by_id(cmd.account_id)
        if not acc:
            raise ValueError(f"Conta '{cmd.account_id}' não localizada.")
        acc.debit(cmd.amount)
        self._repo.save(acc)
        return AccountDto(
            account_id=acc.account_id,
            owner_name=acc.owner_name,
            cpf=acc.cpf,
            pix_key=acc.pix_key,
            balance=acc.balance,
            is_active=acc.is_active,
        )

    def credit(self, cmd: CreditAccountCommand) -> AccountDto:
        acc = self._repo.find_by_id(cmd.account_id)
        if not acc:
            raise ValueError(f"Conta '{cmd.account_id}' não localizada.")
        acc.credit(cmd.amount)
        self._repo.save(acc)
        return AccountDto(
            account_id=acc.account_id,
            owner_name=acc.owner_name,
            cpf=acc.cpf,
            pix_key=acc.pix_key,
            balance=acc.balance,
            is_active=acc.is_active,
        )
