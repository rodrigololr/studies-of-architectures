"""
cli_payment_controller.py - Adaptador Primário CLI / Terminal Console.

Permite que operadores executem liquidações manuais via terminal,
provando que o núcleo da aplicação pode ser acionado por múltiplos adaptadores de entrada
sem nenhuma modificação no código de negócio.
"""

from __future__ import annotations
from domain.models import PaymentRequest
from ports.driver import ProcessPaymentUseCasePort


class CliPaymentController:
    def __init__(self, use_case: ProcessPaymentUseCasePort) -> None:
        self.use_case = use_case

    def run_cli_command(self, order_id: str, amount: float, email: str) -> str:
        req = PaymentRequest(
            payment_id=order_id,
            amount=amount,
            currency="BRL",
            customer_email=email,
            credit_card_token="tok_cli_terminal_mock",
        )
        try:
            res = self.use_case.execute(req)
            return f"[CLI OK] Pedido {res.payment_id} aprovado via {res.provider_used} (Tx: {res.transaction_id})"
        except Exception as e:
            return f"[CLI ERRO] Falha ao processar {order_id}: {e}"
