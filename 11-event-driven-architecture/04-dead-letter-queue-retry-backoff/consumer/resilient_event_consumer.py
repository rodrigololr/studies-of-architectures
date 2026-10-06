"""Resilient Event Consumer com Retry Loop e Desvio para DLQ."""

import time
from typing import Dict, Any, List
from dlq.retry_policy import RetryPolicy
from dlq.dead_letter_queue import DeadLetterQueue, DeadLetterMessage


class ResilientEventConsumer:
    """Consumidor resiliente que previne travamento de fila por mensagens venenosas (Poison Pills)."""

    def __init__(self, retry_policy: RetryPolicy, dlq: DeadLetterQueue) -> None:
        self.retry_policy = retry_policy
        self.dlq = dlq
        self.successfully_processed: List[Dict[str, Any]] = []
        self.transient_error_counters: Dict[str, int] = {}

    def consume_event(self, topic: str, message: Dict[str, Any]) -> str:
        msg_id = message.get("id", "UNKNOWN")
        attempt = 0
        last_error = ""

        # Loop de retentativas com Exponential Backoff
        while self.retry_policy.should_retry(attempt):
            try:
                self._process_business_logic(message)
                self.successfully_processed.append(message)
                return "PROCESSED_SUCCESS"
            except Exception as exc:
                last_error = str(exc)
                delay = self.retry_policy.compute_delay_seconds(attempt)
                time.sleep(delay)  # Backoff
                attempt += 1

        # Todas as retentativas falharam: Desvia a mensagem venenosa para a DLQ
        dl_msg = DeadLetterMessage(
            message_id=msg_id,
            original_topic=topic,
            payload=message,
            error_reason=last_error,
            total_retries_attempted=attempt,
        )
        self.dlq.enqueue_poison_pill(dl_msg)
        return "DIVERTED_TO_DLQ"

    def _process_business_logic(self, message: Dict[str, Any]) -> None:
        msg_id = message.get("id", "")

        # 1. Simulação de Poison Pill fatal (ex: payload corrompido)
        if message.get("is_corrupted"):
            raise ValueError("Payload corrompido: Campo obrigatório 'customer_id' ausente ou inválido.")

        # 2. Simulação de Falha Transitória (ex: falha temporária que se cura após 2 tentativas)
        transient_limit = message.get("transient_glitch_count", 0)
        current_glitches = self.transient_error_counters.get(msg_id, 0)
        if current_glitches < transient_limit:
            self.transient_error_counters[msg_id] = current_glitches + 1
            raise ConnectionError(f"Instabilidade temporária de rede (Tentativa #{current_glitches + 1})")
