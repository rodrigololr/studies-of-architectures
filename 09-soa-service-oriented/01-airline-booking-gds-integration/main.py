"""Ponto de Entrada e Demonstração Executável - Exemplo 01: Airline Booking GDS Integration.

Demonstra os princípios fundamentais da Service-Oriented Architecture (SOA):
1. Service Registry (UDDI / Descoberta dinâmica de serviços).
2. Canonical Data Model (CDM) para neutralidade de schemas.
3. Message Transformation e Protocol Mediation (Tradução de REST/JSON para Terminal TTY Legado).
4. Orquestração corporativa no Enterprise Service Bus (ESB) com transação compensatória.
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from esb.service_registry import ServiceRegistry
from esb.bus_orchestrator import AirlineEnterpriseServiceBus
from services.legacy_gds_service import LegacyGdsService
from services.payment_service import CorporatePaymentService
from services.eticket_service import ETicketIssuanceService


def main() -> None:
    print("=" * 80)
    print(" SERVICE-ORIENTED ARCHITECTURE (SOA) - EXEMPLO 01: AIRLINE GDS & ESB")
    print("=" * 80)

    # 1. Configuração do Service Registry Corporativo (Catálogo de Serviços)
    registry = ServiceRegistry()

    legacy_gds = LegacyGdsService()
    payment_svc = CorporatePaymentService()
    eticket_svc = ETicketIssuanceService()

    registry.register_service(
        name="LegacyGdsService",
        version="1.0-EDICOM",
        protocol="RAW_TTY_SOCKET",
        description="Sistema Legado de Distribuição Global de Inventário (Amadeus / Sabre)",
        instance=legacy_gds,
    )
    registry.register_service(
        name="CorporatePaymentService",
        version="2.4",
        protocol="REST/JSON",
        description="Gateway Corporativo de Liquidação Financeira de Bilhetes",
        instance=payment_svc,
    )
    registry.register_service(
        name="ETicketIssuanceService",
        version="3.1-IATA",
        protocol="IATA_TICKET_SOAP",
        description="Emissor Oficial de Bilhete Eletrônico Padrão IATA 13 Dígitos",
        instance=eticket_svc,
    )

    print("\n--- 1. Serviços Cadastrados no Service Registry Corporativo ---")
    for name, meta in registry.list_services().items():
        print(f" -> [{meta.service_name} v{meta.service_version}] Protocolo: {meta.endpoint_protocol} | {meta.description}")

    # 2. Inicialização do Enterprise Service Bus (ESB)
    esb = AirlineEnterpriseServiceBus(registry=registry)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Emissão Completa com Sucesso (GRU -> MIA)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Solicitação de Reserva Web -> Mediação ESB -> Emissão com Sucesso ---")
    web_request_1 = {
        "passenger": {
            "first_name": "Maria",
            "last_name": "Silva",
            "passport_or_cpf": "FP892341",
            "email": "maria.silva@email.com",
        },
        "flight": {
            "flight_number": "LA3301",
            "origin": "GRU",
            "destination": "MIA",
            "departure_date": "2026-11-20",
            "cabin_class": "Y",
        },
        "card_token": "TOK_VISA_PLATINUM_9912",
        "fare_amount": 3_850.0,
    }

    resp_1 = esb.process_booking_request(web_request_1)
    print(f"Status: {resp_1.status}")
    print(f"Código Localizador (PNR GDS): {resp_1.pnr_code}")
    print(f"Bilhete IATA Oficial: {resp_1.eticket_number}")
    print(f"Código de Autorização Bancária: {resp_1.authorization_code}")
    print(f"Mensagem do ESB: {resp_1.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Falha no Pagamento com Compensação / Rollback no GDS Legado
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Pagamento Recusado com Compensação Automática no Legado ---")
    web_request_recusado = {
        "passenger": {
            "first_name": "João",
            "last_name": "Inadimplente",
            "passport_or_cpf": "FP112233",
            "email": "joao@email.com",
        },
        "flight": {
            "flight_number": "LA4420",
            "origin": "GIG",
            "destination": "FRA",
            "departure_date": "2026-12-05",
            "cabin_class": "J",
        },
        "card_token": "TOK_DECLINED_INSUFFICIENT_LIMIT",
        "fare_amount": 14_200.0,
    }

    resp_2 = esb.process_booking_request(web_request_recusado)
    print(f"Status: {resp_2.status}")
    print(f"PNR Temporário Cancelado: {resp_2.pnr_code}")
    print(f"Mensagem do ESB: {resp_2.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Falha de Governança SOA (Serviço Crítico Indisponível no Registry)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Falha de Descoberta no Registry (Service Not Found) ---")
    empty_registry = ServiceRegistry()
    broken_esb = AirlineEnterpriseServiceBus(registry=empty_registry)
    resp_3 = broken_esb.process_booking_request(web_request_1)
    print(f"Status: {resp_3.status} | Resposta do ESB: {resp_3.message}")

    print("\n" + "=" * 80)
    print(" Exemplo 01 de Service-Oriented Architecture (SOA) finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
