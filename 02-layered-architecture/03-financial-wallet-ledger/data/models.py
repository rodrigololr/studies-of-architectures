"""
models.py - Camada de Dados (Data Layer).
Modelos da Carteira Digital e do Livro-Razão (Ledger) de transações imutáveis.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


@dataclass
class WalletModel:
    wallet_id: str
    user_id: str
    current_balance: float = 0.0


@dataclass(frozen=True)
class LedgerEntryModel:
    entry_id: str
    wallet_id: str
    tx_type: TransactionType
    amount: float
    balance_after: float
    description: str
    timestamp: str
