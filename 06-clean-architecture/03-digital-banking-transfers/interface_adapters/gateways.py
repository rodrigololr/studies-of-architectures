"""
interface_adapters/gateways.py - Camada 3: Gateways e Repositórios Bancários.
"""

from __future__ import annotations
from typing import Dict, Optional, List
from entities.models import Account, Transfer, PixKeyRecord
from use_cases.boundaries import (
    AccountRepositoryGateway,
    PixDirectoryGateway,
    TransferRepositoryGateway,
)


class InMemoryAccountRepository(AccountRepositoryGateway):
    def __init__(self, accounts: Optional[Dict[str, Account]] = None) -> None:
        self._accounts: Dict[str, Account] = dict(accounts or {})

    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        return self._accounts.get(account_number)

    def save(self, account: Account) -> None:
        self._accounts[account.account_number] = account


class InMemoryPixDirectoryGateway(PixDirectoryGateway):
    def __init__(self, directory: Optional[Dict[str, PixKeyRecord]] = None) -> None:
        self._directory: Dict[str, PixKeyRecord] = dict(directory or {})

    def register_key(self, record: PixKeyRecord) -> None:
        self._directory[record.key_value] = record

    def lookup_pix_key(self, pix_key: str) -> Optional[PixKeyRecord]:
        return self._directory.get(pix_key)


class InMemoryTransferRepository(TransferRepositoryGateway):
    def __init__(self) -> None:
        self._transfers: List[Transfer] = []

    def save(self, transfer: Transfer) -> None:
        self._transfers.append(transfer)

    def list_by_account(self, account_number: str) -> List[Transfer]:
        return [
            t for t in self._transfers
            if t.from_account_number == account_number or t.to_account_number == account_number
        ]
