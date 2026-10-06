"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de abertura de carteira, depósito, saque e extrato,
retornando status HTTP adequados.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import WalletService
from business.exceptions import BusinessException, InsufficientFundsException, WalletNotFoundException


class WalletController:
    def __init__(self, service: WalletService) -> None:
        self.service = service

    def open_wallet(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/wallets"""
        try:
            user_id = payload.get("user_id", "")
            wallet = self.service.create_wallet(user_id)
            return {
                "status_code": 201,
                "data": {"wallet_id": wallet.wallet_id, "user_id": wallet.user_id, "balance": wallet.current_balance},
            }
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def deposit(self, wallet_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/wallets/{id}/credit"""
        try:
            amount = float(payload.get("amount", 0.0))
            desc = payload.get("description", "Depósito em conta")
            entry = self.service.credit(wallet_id, amount, desc)
            return {
                "status_code": 200,
                "data": {
                    "entry_id": entry.entry_id,
                    "type": entry.tx_type.value,
                    "amount": entry.amount,
                    "new_balance": entry.balance_after,
                },
            }
        except WalletNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def withdraw(self, wallet_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/wallets/{id}/debit"""
        try:
            amount = float(payload.get("amount", 0.0))
            desc = payload.get("description", "Pagamento de conta")
            entry = self.service.debit(wallet_id, amount, desc)
            return {
                "status_code": 200,
                "data": {
                    "entry_id": entry.entry_id,
                    "type": entry.tx_type.value,
                    "amount": entry.amount,
                    "new_balance": entry.balance_after,
                },
            }
        except InsufficientFundsException as ex:
            # 422 Unprocessable Entity para regra de negócio de saldo
            return {"status_code": 422, "error": str(ex)}
        except WalletNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def get_statement(self, wallet_id: str) -> Dict[str, Any]:
        """GET /api/wallets/{id}/statement"""
        try:
            statement = self.service.get_statement(wallet_id)
            return {"status_code": 200, "data": statement}
        except WalletNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
