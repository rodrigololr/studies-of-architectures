"""
main.py - Ponto de Entrada / Composition Root do Exemplo 01.

Demonstra:
1. Montagem das dependências (Composition Root / Inversão de Controle).
2. Conexão de Adaptadores Secundários (Stripe, Pagar.me, Mercado Pago, Auditoria).
3. Conexão de Adaptadores Primários (HTTP REST Controller, CLI Controller).
4. Cenários de Fallback em tempo de execução quando provedores oscilam.
"""

import sys
import json
from pathlib import Path

# Garante importações relativas limpas
sys.path.insert(0, str(Path(__file__).parent))

from adapters.secondary.stripe_adapter import StripePaymentAdapter
from adapters.secondary.pagarme_adapter import PagarMePaymentAdapter
from adapters.secondary.mercadopago_adapter import MercadoPagoPaymentAdapter
from adapters.secondary.in_memory_audit_adapter import InMemoryPaymentAuditAdapter
from core.service import PaymentMultiplexerService
from adapters.primary.http_payment_controller import HttpPaymentController
from adapters.primary.cli_payment_controller import CliPaymentController


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 01: PAYMENT GATEWAY MULTIPLEXER")
    print("=" * 80)

    # 1. Instanciação dos Adaptadores Secundários (Driven Adapters)
    stripe = StripePaymentAdapter(api_key="sk_live_stripe_secret_123")
    pagarme = PagarMePaymentAdapter(encryption_key="ek_live_pagarme_xyz")
    mercadopago = MercadoPagoPaymentAdapter(access_token="app_mp_access_999")
    audit_repo = InMemoryPaymentAuditAdapter()

    # 2. Instanciação do Núcleo da Aplicação (Core / Hexágono)
    # A ordem da lista define a prioridade de roteamento/fallback
    multiplexer_service = PaymentMultiplexerService(
        gateways_in_priority_order=[stripe, pagarme, mercadopago],
        audit_repository=audit_repo,
    )

    # 3. Instanciação dos Adaptadores Primários (Driver Adapters)
    http_controller = HttpPaymentController(use_case=multiplexer_service)
    cli_controller = CliPaymentController(use_case=multiplexer_service)

    print("\n--- CENÁRIO 1: Transação normal (Stripe saudável e prioritário) ---")
    status_code, body = http_controller.handle_post_charge({
        "order_id": "ORD-1001",
        "amount": 250.00,
        "currency": "BRL",
        "email": "cliente.feliz@email.com",
        "card_token": "tok_visa_4242",
    })
    print(f"HTTP Status: {status_code}")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Simulação de Falha do Provedor 1 (Stripe cai) -> Fallback Pagar.me ---")
    stripe.set_availability(False)
    print("[Simulação] Provedor Stripe marcado como OFFLINE (Healthcheck falhou).")

    status_code, body = http_controller.handle_post_charge({
        "order_id": "ORD-1002",
        "amount": 1200.50,
        "currency": "BRL",
        "email": "cliente.vip@email.com",
        "card_token": "tok_master_8888",
    })
    print(f"HTTP Status: {status_code}")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Simulação de Falha Dupla (Stripe e Pagar.me caem) -> Fallback Mercado Pago ---")
    pagarme.set_availability(False)
    print("[Simulação] Provedor Pagar.me também marcado como OFFLINE.")

    status_code, body = http_controller.handle_post_charge({
        "order_id": "ORD-1003",
        "amount": 89.90,
        "currency": "BRL",
        "email": "comprador.urgente@email.com",
        "card_token": "tok_elo_1111",
    })
    print(f"HTTP Status: {status_code}")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Acionamento via Adaptador Secundário Alternativo (CLI Terminal) ---")
    cli_output = cli_controller.run_cli_command(
        order_id="ORD-CLI-99",
        amount=450.00,
        email="operador.suporte@loja.com",
    )
    print(cli_output)

    print("\n--- CENÁRIO 5: Rejeição por Regra de Domínio (Valor Negativo) ---")
    status_code, body = http_controller.handle_post_charge({
        "order_id": "ORD-INVALID-01",
        "amount": -50.00,
        "currency": "BRL",
        "email": "teste@email.com",
    })
    print(f"HTTP Status: {status_code}")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 6: Auditoria Persistida no Repositório Secundário ---")
    records = audit_repo.list_history()
    print(f"Total de transações auditadas no repositório: {len(records)}")
    for r in records:
        print(f" -> [{r.processed_at.strftime('%H:%M:%S')}] {r.payment_id}: {r.amount} {r.currency} via '{r.provider_used}' (Tx: {r.transaction_id})")

    print("\n" + "=" * 80)
    print(" Demonstração concluída com sucesso! Núcleo isolado de detalhes técnicos.")
    print("=" * 80)


if __name__ == "__main__":
    main()
