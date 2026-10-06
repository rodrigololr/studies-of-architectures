"""Idempotent Consumer de Webhooks de Pagamento."""

from typing import Dict, Any
from events.payment_events import PaymentWebhookEvent
from store.deduplication_store import IdempotencyStore


class IdempotentPaymentConsumer:
    """Consumidor que garante processamento com efeito único (Exactly-Once Semantics via Idempotência)."""

    def __init__(self, idempotency_store: IdempotencyStore) -> None:
        self._store = idempotency_store
        # Ledger contábil de saldos dos clientes
        self._customer_balances: Dict[str, float] = {
            "CUST-ALICE": 100.0,
            "CUST-BOB": 50.0,
        }
        # Métricas de observabilidade
        self.total_received: int = 0
        self.actual_processed: int = 0
        self.duplicates_ignored: int = 0

    def process_payment_webhook(self, event: PaymentWebhookEvent) -> Dict[str, Any]:
        self.total_received += 1
        idempotency_key = event.event_id

        # 1. Verificação Atômica no Deduplication Store
        is_first_delivery = self._store.try_claim_key(idempotency_key)

        if not is_first_delivery:
            # Evento duplicado detectado! Retorna o resultado anterior sem alterar o saldo
            self.duplicates_ignored += 1
            cached_result = self._store.get_cached_result(idempotency_key) or {}
            return {
                "event_id": idempotency_key,
                "status": "DUPLICATE_IGNORED",
                "message": "Mensagem duplicada descartada com segurança sem efeitos colaterais.",
                "cached_result": cached_result,
                "current_balance": self._customer_balances.get(event.customer_id, 0.0),
            }

        # 2. Primeira Entrega: Executa a regra de negócio contábil
        self.actual_processed += 1
        current = self._customer_balances.get(event.customer_id, 0.0)
        new_balance = round(current + event.amount, 2)
        self._customer_balances[event.customer_id] = new_balance

        result_payload = {
            "event_id": idempotency_key,
            "payment_intent": event.payment_intent_id,
            "customer_id": event.customer_id,
            "amount_credited": event.amount,
            "new_balance": new_balance,
            "status": "CREDITED",
        }

        # 3. Registra o resultado para futuras consultas duplicadas
        self._store.mark_processed(idempotency_key, result_payload)

        return result_payload

    def get_customer_balance(self, customer_id: str) -> float:
        return self._customer_balances.get(customer_id, 0.0)
