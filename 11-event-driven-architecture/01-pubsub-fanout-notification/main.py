"""Demonstração de EDA: Pub/Sub Fan-out de Notificações com Múltiplos Consumidores.

Cenários demonstrados:
1. Emissão de evento de pedido (OrderPlacedEvent) com dispersão Fan-out para 4 canais simultâneos
   (Email, SMS, Push Notification e Analytics)
2. Processamento de segundo pedido com agregação de métricas de negócio (GMV e Ticket Médio)
3. Extensibilidade dinâmica: Conexão de um novo consumidor (Auditoria) sem alterar o produtor
4. Métricas consolidadas do broker de mensageria
"""

import sys
from pathlib import Path
from typing import Any

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from broker.pubsub_broker import PubSubBroker
from events.order_events import OrderItem
from producer.checkout_producer import CheckoutService
from consumers.email_consumer import EmailNotificationConsumer
from consumers.sms_consumer import SmsNotificationConsumer
from consumers.push_consumer import PushNotificationConsumer
from consumers.analytics_consumer import RealTimeAnalyticsConsumer


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Barramento Pub/Sub de Mensageria e Consumidores Fan-out...")

    # 1. Barramento de Mensageria (Tópicos Pub/Sub)
    broker = PubSubBroker()

    # 2. Produtor (Desacoplado)
    checkout_svc = CheckoutService(broker)

    # 3. Consumidores Independentes
    email_consumer = EmailNotificationConsumer()
    sms_consumer = SmsNotificationConsumer()
    push_consumer = PushNotificationConsumer()
    analytics_consumer = RealTimeAnalyticsConsumer()

    # Inscrição dos 4 consumidores no tópico "orders.v1" (Fan-out)
    broker.subscribe("orders.v1", email_consumer.handle)
    broker.subscribe("orders.v1", sms_consumer.handle)
    broker.subscribe("orders.v1", push_consumer.handle)
    broker.subscribe("orders.v1", analytics_consumer.handle)

    # -------------------------------------------------------------------------
    # Cenário 1: Pedido #1 (Alice) - Fan-out em 4 Canais
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Conclusão do Pedido #1 de Alice (Fan-out para 4 Consumidores)")
    items_alice = (
        OrderItem("PROD-MON-01", "Monitor 4K 27''", 1, 2100.0),
        OrderItem("PROD-MOU-02", "Mouse Sem Fio Ergonômico", 1, 250.0),
    )
    ev1 = checkout_svc.complete_order(
        order_id="ORD-2026-001",
        customer_id="CUST-ALICE-10",
        customer_name="Alice Silva",
        customer_email="alice@techcorp.com",
        customer_phone="+55 11 98888-1111",
        items=items_alice,
    )
    print(f"Evento Emitido: OrderPlacedEvent [ID: {ev1.order_id}] | Total: R$ {ev1.total_amount:,.2f}")
    print(f"  - [EMAIL] Enviado para {email_consumer.sent_emails[-1]['to']} | Assunto: {email_consumer.sent_emails[-1]['subject']}")
    print(f"  - [SMS]   Enviado para {sms_consumer.sent_sms[-1]['phone']} | Texto: '{sms_consumer.sent_sms[-1]['message']}'")
    print(f"  - [PUSH]  Notificação enviada para User: {push_consumer.sent_pushes[-1]['target_user_id']}")
    print(f"  - [ANALYTICS] GMV Atual: R$ {analytics_consumer.accumulated_gmv_brl:,.2f} | Pedidos: {analytics_consumer.total_orders_count}")

    assert len(email_consumer.sent_emails) == 1
    assert len(sms_consumer.sent_sms) == 1
    assert len(push_consumer.sent_pushes) == 1
    assert analytics_consumer.total_orders_count == 1
    assert analytics_consumer.accumulated_gmv_brl == 2350.0

    # -------------------------------------------------------------------------
    # Cenário 2: Pedido #2 (Bob) - Atualização de Métricas
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Conclusão do Pedido #2 de Bob e Atualização de Métricas")
    items_bob = (
        OrderItem("PROD-CHAIR-05", "Cadeira Gamer Reclinável", 1, 1650.0),
    )
    checkout_svc.complete_order(
        order_id="ORD-2026-002",
        customer_id="CUST-BOB-20",
        customer_name="Bob Souza",
        customer_email="bob@developer.net",
        customer_phone="+55 11 97777-2222",
        items=items_bob,
    )
    print(f"Total de E-mails enviados:  {len(email_consumer.sent_emails)}")
    print(f"Total de SMS enviados:      {len(sms_consumer.sent_sms)}")
    print(f"Total de Pushes enviados:   {len(push_consumer.sent_pushes)}")
    print(f"Métricas Analytics:")
    print(f"  Total de Pedidos: {analytics_consumer.total_orders_count}")
    print(f"  GMV Acumulado:    R$ {analytics_consumer.accumulated_gmv_brl:,.2f}")
    print(f"  Ticket Médio:     R$ {analytics_consumer.average_ticket_brl:,.2f}")
    assert analytics_consumer.total_orders_count == 2
    assert analytics_consumer.accumulated_gmv_brl == 4000.0
    assert analytics_consumer.average_ticket_brl == 2000.0

    # -------------------------------------------------------------------------
    # Cenário 3: Extensibilidade Dinâmica - Conexão do 5º Consumidor (Auditoria)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Extensibilidade em Tempo Real (Adicionando Consumidor de Auditoria)")
    audit_log = []

    def audit_consumer(event: Any) -> None:
        audit_log.append(f"AUDIT-RECORD: Pedido {event.order_id} registrado com sucesso para {event.customer_name}.")

    # Registra dinamicamente sem reiniciar ou tocar no CheckoutService
    broker.subscribe("orders.v1", audit_consumer)
    print("Consumidor de Auditoria inscrito com sucesso no tópico 'orders.v1'.")

    # Pedido #3 de Carol
    checkout_svc.complete_order(
        order_id="ORD-2026-003",
        customer_id="CUST-CAROL-30",
        customer_name="Carol Mendes",
        customer_email="carol@design.org",
        customer_phone="+55 11 96666-3333",
        items=(OrderItem("PROD-KEY-03", "Teclado Mecânico RGB", 1, 400.0),),
    )
    print(f"Registro capturado pelo Consumidor de Auditoria: '{audit_log[-1]}'")
    assert len(audit_log) == 1
    assert len(email_consumer.sent_emails) == 3

    # -------------------------------------------------------------------------
    # Cenário 4: Métricas do Broker
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Métricas Globais de Despacho do Barramento Pub/Sub")
    print(f"Mensagens Publicadas no Tópico:  {broker.published_messages_count}")
    print(f"Total de Entregas Efetuadas:     {broker.total_dispatches_count} (Fan-out comprovado: 4 + 4 + 5 = 13)")
    assert broker.published_messages_count == 3
    assert broker.total_dispatches_count == 13

    print_separator("Todos os cenários de Pub/Sub Fan-out foram validados com sucesso!")


if __name__ == "__main__":
    main()
