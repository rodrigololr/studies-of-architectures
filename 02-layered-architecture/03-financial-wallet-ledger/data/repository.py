"""
repository.py - Camada de Dados (Data Layer).
Repositórios para controle de saldos da carteira e append-only do ledger financeiro.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from data.models import WalletModel, LedgerEntryModel


class WalletRepository:
    def __init__(self) -> None:
        self._wallets: Dict[str, WalletModel] = {}

    def save(self, wallet: WalletModel) -> WalletModel:
        self._wallets[wallet.wallet_id] = wallet
        return wallet

    def find_by_id(self, wallet_id: str) -> Optional[WalletModel]:
        return self._wallets.get(wallet_id)


class LedgerRepository:
    def __init__(self) -> None:
        # Tabela Append-Only: lançamentos nunca são alterados ou deletados
        self._entries: List[LedgerEntryModel] = []

    def record(self, entry: LedgerEntryModel) -> LedgerEntryModel:
        self._entries.append(entry)
        return entry

    def list_by_wallet(self, wallet_id: str) -> List[LedgerEntryModel]:
        return [e for e in self._entries if e.wallet_id == wallet_id]
