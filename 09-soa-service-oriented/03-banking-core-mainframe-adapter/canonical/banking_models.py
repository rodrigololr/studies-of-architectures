"""Canonical Data Model (CDM) - Modelo Canônico de Transações Bancárias."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AccountIdentification:
    branch_code: str      # Agência (4 dígitos, ex: "0142")
    account_number: str   # Conta Corrente (7 dígitos, ex: "0099120")


@dataclass(frozen=True)
class CanonicalTransactionRequest:
    transaction_id: str
    account: AccountIdentification
    transaction_type: str  # "D" (Débito), "C" (Crédito)
    amount_brl: float
    original_currency: str = "BRL"


@dataclass(frozen=True)
class CanonicalTransactionResponse:
    transaction_id: str
    is_success: bool
    return_code: str
    new_balance_brl: float
    auth_stamp: str
    message: str
