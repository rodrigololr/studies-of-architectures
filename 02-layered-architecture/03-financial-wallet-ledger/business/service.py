"""
service.py - Camada de Negócio (Business Layer).

Responsável por:
- Criar carteira digital com validação inicial.
- Executar crédito financeiro atualizando saldo e registrando lançamento no Ledger.
- Executar débito com validação rigorosa de saldo suficiente.
- Emitir extrato financeiro auditável consolidado.
"""

from __future__ import annotations
from datetime import datetime
import uuid
from typing import Dict, List
from business.exceptions import (
    WalletNotFoundException,
    InsufficientFundsException,
    InvalidAmountException,
)
from data.models import WalletModel, LedgerEntryModel, TransactionType
from data.repository import WalletRepository, LedgerRepository


class WalletService:
    def __init__(self, wallet_repo: WalletRepository, ledger_repo: LedgerRepository) -> None:
        self.wallet_repo = wallet_repo
        self.ledger_repo = ledger_repo

    def create_wallet(self, user_id: str) -> WalletModel:
        wallet = WalletModel(wallet_id=str(uuid.uuid4())[:8], user_id=user_id, current_balance=0.0)
        return self.wallet_repo.save(wallet)

    def credit(self, wallet_id: str, amount: float, description: str) -> LedgerEntryModel:
        if amount <= 0:
            raise InvalidAmountException("O valor do crédito deve ser estritamente positivo.")

        wallet = self.wallet_repo.find_by_id(wallet_id)
        if not wallet:
            raise WalletNotFoundException(f"Carteira com ID '{wallet_id}' não encontrada.")

        wallet.current_balance = round(wallet.current_balance + amount, 2)
        self.wallet_repo.save(wallet)

        entry = LedgerEntryModel(
            entry_id=str(uuid.uuid4())[:8],
            wallet_id=wallet_id,
            tx_type=TransactionType.CREDIT,
            amount=amount,
            balance_after=wallet.current_balance,
            description=description,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return self.ledger_repo.record(entry)

    def debit(self, wallet_id: str, amount: float, description: str) -> LedgerEntryModel:
        if amount <= 0:
            raise InvalidAmountException("O valor do débito deve ser estritamente positivo.")

        wallet = self.wallet_repo.find_by_id(wallet_id)
        if not wallet:
            raise WalletNotFoundException(f"Carteira com ID '{wallet_id}' não encontrada.")

        # Regra Invariante: Saldo nunca pode ficar negativo
        if wallet.current_balance < amount:
            raise InsufficientFundsException(
                f"Saldo insuficiente. Saldo atual: R$ {wallet.current_balance:.2f}, Débito solicitado: R$ {amount:.2f}."
            )

        wallet.current_balance = round(wallet.current_balance - amount, 2)
        self.wallet_repo.save(wallet)

        entry = LedgerEntryModel(
            entry_id=str(uuid.uuid4())[:8],
            wallet_id=wallet_id,
            tx_type=TransactionType.DEBIT,
            amount=amount,
            balance_after=wallet.current_balance,
            description=description,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return self.ledger_repo.record(entry)

    def get_statement(self, wallet_id: str) -> Dict[str, object]:
        wallet = self.wallet_repo.find_by_id(wallet_id)
        if not wallet:
            raise WalletNotFoundException(f"Carteira '{wallet_id}' inexistente.")

        entries = self.ledger_repo.list_by_wallet(wallet_id)
        return {
            "wallet_id": wallet.wallet_id,
            "user_id": wallet.user_id,
            "balance": wallet.current_balance,
            "entries_count": len(entries),
            "history": [
                {
                    "id": e.entry_id,
                    "type": e.tx_type.value,
                    "amount": e.amount,
                    "balance_after": e.balance_after,
                    "description": e.description,
                    "timestamp": e.timestamp,
                }
                for e in entries
            ],
        }
