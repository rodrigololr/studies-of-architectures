"""Demonstração de EDA: Idempotent Consumer & Desduplicação Atômica de Eventos.

Cenários demonstrados:
1. Primeira entrega de Webhook PIX/Cartão: saldo creditado com sucesso
2. Retentativa de rede do gateway (mesmo event_id): detecção de duplicata e proteção de saldo
3. Rajada de 5 retransmissões idênticas: nenhuma duplicação contábil ocorre
4. Processamento de novo evento legítimo para outro cliente
5. Métricas de observabilidade de desduplicação
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from store.deduplication_store import IdempotencyStore
from events.payment_events import PaymentWebhookEvent
from consumer.idempotent_payment_consumer import IdempotentPaymentConsumer


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Consumidor Idempotente e Deduplication Store...")

    # 1. Repositório de Idempotência Atômico
    store = IdempotencyStore()

    # 2. Consumidor Contábil de Webhooks
    consumer = IdempotentPaymentConsumer(store)

    # -------------------------------------------------------------------------
    # Cenário 1: Primeira Entrega do Webhook de R$ 250,00 (Alice)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Primeira Entrega de Webhook PIX para Alice (R$ 250,00)")
    evt_alice = PaymentWebhookEvent(
        event_id="evt_pix_1001",
        payment_intent_id="pi_stripe_alpha_01",
        customer_id="CUST-ALICE",
        amount=250.00,
    )
    print(f"Saldo Inicial de Alice: R$ {consumer.get_customer_balance('CUST-ALICE'):.2f}")
    res1 = consumer.process_payment_webhook(evt_alice)
    print(f"Resultado do Processamento: {res1['status']}")
    print(f"Novo Saldo de Alice: R$ {consumer.get_customer_balance('CUST-ALICE'):.2f}")
    assert res1["status"] == "CREDITED"
    assert consumer.get_customer_balance("CUST-ALICE") == 350.00
    assert consumer.actual_processed == 1

    # -------------------------------------------------------------------------
    # Cenário 2: Retransmissão de Rede Imediata (Mesmo Event ID)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Retransmissão do Mesmo Evento por Falha de ACK de Rede")
    res2 = consumer.process_payment_webhook(evt_alice)
    print(f"Resultado da Retransmissão: {res2['status']}")
    print(f"Mensagem: {res2['message']}")
    print(f"Saldo de Alice permanece INALTERADO: R$ {consumer.get_customer_balance('CUST-ALICE'):.2f}")
    assert res2["status"] == "DUPLICATE_IGNORED"
    assert consumer.get_customer_balance("CUST-ALICE") == 350.00
    assert consumer.duplicates_ignored == 1

    # -------------------------------------------------------------------------
    # Cenário 3: Rajada de 5 Retentativas Idênticas
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Rajada de 5 Retentativas Sucessivas (Stress de Duplicatas)")
    for i in range(1, 6):
        res_burst = consumer.process_payment_webhook(evt_alice)
        print(f"  Tentativa #{i+2} -> {res_burst['status']} (Saldo seguro: R$ {consumer.get_customer_balance('CUST-ALICE'):.2f})")
        assert res_burst["status"] == "DUPLICATE_IGNORED"

    assert consumer.duplicates_ignored == 6
    assert consumer.get_customer_balance("CUST-ALICE") == 350.00

    # -------------------------------------------------------------------------
    # Cenário 4: Novo Evento Legítimo (Bob: R$ 500,00)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Novo Evento Distinto para Outro Cliente (Bob)")
    evt_bob = PaymentWebhookEvent(
        event_id="evt_pix_2002",
        payment_intent_id="pi_stripe_beta_02",
        customer_id="CUST-BOB",
        amount=500.00,
    )
    print(f"Saldo Inicial de Bob: R$ {consumer.get_customer_balance('CUST-BOB'):.2f}")
    res_bob = consumer.process_payment_webhook(evt_bob)
    print(f"Resultado: {res_bob['status']}")
    print(f"Novo Saldo de Bob: R$ {consumer.get_customer_balance('CUST-BOB'):.2f}")
    assert res_bob["status"] == "CREDITED"
    assert consumer.get_customer_balance("CUST-BOB") == 550.00

    # -------------------------------------------------------------------------
    # Cenário 5: Métricas de Telemetria
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Métricas Consolidadas de Desduplicação")
    print(f"Total de Mensagens Recebidas:       {consumer.total_received}")
    print(f"Eventos Efetivamente Processados:   {consumer.actual_processed}")
    print(f"Duplicatas Bloqueadas com Segurança:{consumer.duplicates_ignored}")
    assert consumer.total_received == 8
    assert consumer.actual_processed == 2
    assert consumer.duplicates_ignored == 6

    print_separator("Todos os cenários do Consumidor Idempotente foram validados com sucesso!")


if __name__ == "__main__":
    main()
