"""
main.py - Composition Root e Demonstração do Exemplo 02.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from domain.models import ChannelType
from core.service import NotificationDispatcherService
from adapters.secondary.sendgrid_email_adapter import SendGridEmailAdapter
from adapters.secondary.twilio_sms_adapter import TwilioSmsAdapter
from adapters.secondary.whatsapp_business_adapter import WhatsAppBusinessAdapter
from adapters.secondary.jinja_template_adapter import SimpleTemplateEngineAdapter
from adapters.secondary.in_memory_history_adapter import InMemoryNotificationHistoryAdapter
from adapters.primary.rest_api_adapter import NotificationRestController
from adapters.primary.event_subscriber_adapter import SecurityEventSubscriberAdapter


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 02: MULTI-CHANNEL NOTIFICATION SERVICE")
    print("=" * 80)

    # 1. Adaptadores Secundários (Driven)
    email_adapter = SendGridEmailAdapter(api_key="SG.test_key_abc")
    sms_adapter = TwilioSmsAdapter(account_sid="AC_twilio_123", auth_token="tok_xyz")
    whatsapp_adapter = WhatsAppBusinessAdapter(phone_number_id="wa_id_99", bearer_token="ea_meta_token")
    template_engine = SimpleTemplateEngineAdapter()
    history_repo = InMemoryNotificationHistoryAdapter()

    channels_map = {
        ChannelType.EMAIL: email_adapter,
        ChannelType.SMS: sms_adapter,
        ChannelType.WHATSAPP: whatsapp_adapter,
    }

    # 2. Núcleo da Aplicação (Core / Hexágono)
    service = NotificationDispatcherService(
        channels=channels_map,
        template_engine=template_engine,
        history_repo=history_repo,
    )

    # 3. Adaptadores Primários (Driver)
    rest_controller = NotificationRestController(use_case=service)
    event_subscriber = SecurityEventSubscriberAdapter(use_case=service)

    print("\n--- CENÁRIO 1: Despacho 2FA com WhatsApp Saudável (Prioritário) ---")
    status, res = rest_controller.handle_post_notify({
        "recipient": {
            "user_id": "usr-101",
            "name": "Mariana Silva",
            "phone": "+5511999998888",
            "email": "mariana@tech.com",
        },
        "template": "auth.2fa_token",
        "params": {"code": "739201", "expires_minutes": 5},
        "priority": "CRITICAL_2FA",
        "preferred_channels": ["WHATSAPP", "SMS", "EMAIL"],
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 2: Falha do WhatsApp -> Fallback Automático para SMS ---")
    whatsapp_adapter.set_healthy(False)
    print("[Simulação] Meta WhatsApp Cloud API fora do ar (503 Service Unavailable).")

    status, res = rest_controller.handle_post_notify({
        "recipient": {
            "user_id": "usr-102",
            "name": "Carlos Eduardo",
            "phone": "+5521988887777",
            "email": "carlos@empresa.com",
        },
        "template": "auth.2fa_token",
        "params": {"code": "194820", "expires_minutes": 5},
        "priority": "CRITICAL_2FA",
        "preferred_channels": ["WHATSAPP", "SMS", "EMAIL"],
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 3: Falha do WhatsApp e SMS -> Fallback para Email ---")
    sms_adapter.set_healthy(False)
    print("[Simulação] Twilio SMS também fora do ar.")

    status, res = rest_controller.handle_post_notify({
        "recipient": {
            "user_id": "usr-103",
            "name": "Renata Lima",
            "phone": "+5531977776666",
            "email": "renata@startup.io",
        },
        "template": "auth.2fa_token",
        "params": {"code": "882310", "expires_minutes": 5},
        "priority": "CRITICAL_2FA",
        "preferred_channels": ["WHATSAPP", "SMS", "EMAIL"],
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 4: Acionamento via Consumidor de Eventos (Event Broker) ---")
    # Restaura canais
    whatsapp_adapter.set_healthy(True)
    sms_adapter.set_healthy(True)
    event_subscriber.on_security_incident_event({
        "event_type": "user.security_alert",
        "user": {
            "id": "usr-999",
            "name": "Julio Verne",
            "email": "julio@aventura.org",
            "phone": "+5541999112233",
        },
        "ip_address": "189.44.120.15",
        "location": "Moscou, Rússia",
    })

    print("\n--- CENÁRIO 5: Rejeição por Destinatário Inválido (Regra de Domínio) ---")
    status, res = rest_controller.handle_post_notify({
        "recipient": {
            "user_id": "usr-void",
            "name": "Sem Contato",
            "phone": "",
            "email": "",
        },
        "template": "auth.2fa_token",
        "params": {"code": "000000", "expires_minutes": 1},
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 6: Auditoria do Histórico no Repositório Secundário ---")
    history = history_repo.get_history()
    print(f"Total de notificações registradas: {len(history)}")
    for item in history:
        print(f" -> [{item.dispatched_at.strftime('%H:%M:%S')}] User: {item.recipient_user_id} | Canal: {item.channel_used.value:10} | Status: {item.status.value}")

    print("\n" + "=" * 80)
    print(" Exemplo 02 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
