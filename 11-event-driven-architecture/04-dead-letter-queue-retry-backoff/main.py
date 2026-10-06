"""Demonstração de EDA: Dead-Letter Queue (DLQ) & Exponential Backoff.

Cenários demonstrados:
1. Mensagem Saudável: Processada imediatamente na primeira tentativa com sucesso
2. Falha Transitória de Rede: Recuperada automaticamente após 2 retentativas com backoff exponencial
3. Mensagem Venenosa (Poison Pill): Esgotamento de 3 retentativas e desvio seguro para a DLQ
4. Desbloqueio da Fila: Próxima mensagem saudável processada normalmente sem bloqueio de fila
5. Auditoria e inspeção das mensagens retidas na DLQ
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from dlq.retry_policy import RetryPolicy
from dlq.dead_letter_queue import DeadLetterQueue
from consumer.resilient_event_consumer import ResilientEventConsumer


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Consumidor Resiliente, Política de Retry e Dead-Letter Queue...")

    # Política de Retry: 3 tentativas com backoff exponencial a partir de 10ms
    retry_policy = RetryPolicy(
        max_retries=3,
        initial_delay_ms=10.0,
        backoff_multiplier=2.0,
        max_delay_ms=500.0,
    )

    dlq = DeadLetterQueue()
    consumer = ResilientEventConsumer(retry_policy=retry_policy, dlq=dlq)

    # -------------------------------------------------------------------------
    # Cenário 1: Mensagem Saudável (Sucesso Imediato)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Mensagem Normal (Sucesso na 1ª Tentativa)")
    msg1 = {"id": "MSG-001", "action": "CREATE_INVOICE", "amount": 1500.0}
    res1 = consumer.consume_event("invoices.v1", msg1)
    print(f"Status do Processamento: {res1}")
    print(f"Total de mensagens na DLQ: {len(dlq.all_messages)}")
    assert res1 == "PROCESSED_SUCCESS"
    assert len(dlq.all_messages) == 0

    # -------------------------------------------------------------------------
    # Cenário 2: Falha Transitória de Rede (Autocura com Retry)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Falha Transitória com Autocura após 2 Retentativas")
    msg2 = {
        "id": "MSG-002",
        "action": "SEND_WEBHOOK",
        "transient_glitch_count": 2,  # Falha 2 vezes e sucede na 3ª
    }
    res2 = consumer.consume_event("webhooks.v1", msg2)
    print(f"Status do Processamento: {res2}")
    print(f"Total de falhas transitórias registradas: {consumer.transient_error_counters['MSG-002']}")
    assert res2 == "PROCESSED_SUCCESS"
    assert consumer.transient_error_counters["MSG-002"] == 2
    assert len(dlq.all_messages) == 0

    # -------------------------------------------------------------------------
    # Cenário 3: Mensagem Venenosa (Poison Pill) Desviada para DLQ
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Mensagem Venenosa (Poison Pill Corrompida) -> Desvio para DLQ")
    msg_poison = {
        "id": "MSG-POISON-666",
        "action": "CORRUPTED_EVENT",
        "is_corrupted": True,
    }
    res_poison = consumer.consume_event("critical.v1", msg_poison)
    print(f"Status do Processamento: {res_poison}")
    print(f"Mensagens na DLQ após desvio: {len(dlq.all_messages)}")
    assert res_poison == "DIVERTED_TO_DLQ"
    assert len(dlq.all_messages) == 1

    # -------------------------------------------------------------------------
    # Cenário 4: Fila Desbloqueada (Head-of-Line Blocking Evitado)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Próxima Mensagem Saudável Processada Normalmente (Fila Desimpedida)")
    msg4 = {"id": "MSG-004", "action": "UPDATE_PROFILE", "user": "alice"}
    res4 = consumer.consume_event("users.v1", msg4)
    print(f"Status do Processamento da Mensagem Seguinte: {res4}")
    assert res4 == "PROCESSED_SUCCESS"
    assert len(consumer.successfully_processed) == 3

    # -------------------------------------------------------------------------
    # Cenário 5: Auditoria e Inspeção da Dead-Letter Queue
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Inspeção e Detalhes da Mensagem Quarentenada na DLQ")
    quarantined = dlq.get_message("MSG-POISON-666")
    assert quarantined is not None
    print(f"ID da Mensagem Quarentenada:  {quarantined.message_id}")
    print(f"Tópico de Origem:            {quarantined.original_topic}")
    print(f"Total de Retries Tentados:   {quarantined.total_retries_attempted}")
    print(f"Causa do Erro Arquivada:     {quarantined.error_reason}")
    print(f"Payload da Mensagem:         {quarantined.payload}")
    assert quarantined.total_retries_attempted == 3
    assert "Payload corrompido" in quarantined.error_reason

    print_separator("Todos os cenários de Retry com Backoff e DLQ foram validados com sucesso!")


if __name__ == "__main__":
    main()
