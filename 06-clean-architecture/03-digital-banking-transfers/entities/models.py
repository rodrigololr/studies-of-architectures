"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Tuple


class TransferMethod(str, Enum):
    PIX = "PIX"
    TED = "TED"


class TransferStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Account:
    account_number: str
    owner_name: str
    balance: float
    daytime_limit: float = 5000.0
    nighttime_limit: float = 1000.0
    is_blocked: bool = False

    def check_transfer_eligibility(self, amount: float, is_night_time: bool) -> Tuple[bool, Optional[str]]:
        """
        Regra Corporativa de Negócio:
        Verifica saldo, bloqueio cadastral e limites de horário do Banco Central.
        """
        if self.is_blocked:
            return False, f"A conta {self.account_number} está bloqueada para movimentações financeiras."

        if amount <= 0:
            return False, "O valor da transferência deve ser estritamente positivo."

        if self.balance < amount:
            return False, f"Saldo insuficiente (Saldo atual: R$ {self.balance:.2f}, Solicitado: R$ {amount:.2f})."

        effective_limit = self.nighttime_limit if is_night_time else self.daytime_limit
        if amount > effective_limit:
            periodo = "noturno (20h às 06h)" if is_night_time else "diurno"
            return False, f"Valor de R$ {amount:.2f} excede o limite {periodo} de R$ {effective_limit:.2f}."

        return True, None

    def debit(self, amount: float) -> None:
        self.balance = round(self.balance - amount, 2)

    def credit(self, amount: float) -> None:
        self.balance = round(self.balance + amount, 2)


@dataclass(frozen=True)
class PixKeyRecord:
    key_value: str
    key_type: str  # CPF, EMAIL, PHONE, EVP
    account_number: str


@dataclass(frozen=True)
class Transfer:
    transfer_id: str
    from_account_number: str
    to_account_number: str
    amount: float
    method: TransferMethod
    status: TransferStatus
    transacted_at: datetime
    error_reason: Optional[str] = None
