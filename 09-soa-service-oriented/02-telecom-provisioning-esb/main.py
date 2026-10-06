"""Ponto de Entrada e Demonstração Executável - Exemplo 02: Telecom Provisioning ESB.

Demonstra:
1. Orquestração corporativa heterogênea via ESB (MML de Rede Celular, Inventário de SIMs e Billing).
2. Modelo Canônico de Provisionamento de Telecomunicações (CDM).
3. Transação compensatória (Saga no ESB) desprovisionando antena e chip em caso de falha de cobrança.
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from esb.service_registry import TelecomServiceRegistry
from esb.bus_orchestrator import TelecomProvisioningESB
from services.sim_inventory_service import SimCardInventoryService
from services.network_hlr_service import NetworkHlrService
from services.billing_platform_service import BillingPlatformService


def main() -> None:
    print("=" * 80)
    print(" SERVICE-ORIENTED ARCHITECTURE (SOA) - EXEMPLO 02: TELECOM PROVISIONING ESB")
    print("=" * 80)

    # 1. Configuração do Service Registry e Serviços Participantes
    registry = TelecomServiceRegistry()

    inventory_svc = SimCardInventoryService()
    hlr_svc = NetworkHlrService()
    billing_svc = BillingPlatformService()

    registry.register(
        name="SimCardInventoryService",
        version="1.4",
        protocol="INTERNAL_INVENTORY_API",
        desc="Sistema de Almoxarifado e Gestão de Lotes de Chips Físicos (ICCID)",
        instance=inventory_svc,
    )
    registry.register(
        name="NetworkHlrService",
        version="5.0-5G_CORE",
        protocol="MML_TELNET_DAEMON",
        desc="Central Core de Rede Celular e Roteamento de Antenas HLR/HSS",
        instance=hlr_svc,
    )
    registry.register(
        name="BillingPlatformService",
        version="3.2",
        protocol="SOAP_XML_BILLING",
        desc="Motor Corporativo de Faturamento, Planos e Ciclos de Cobrança",
        instance=billing_svc,
    )

    print("\n--- 1. Serviços de Telecomunicações Descobertos via Registry ---")
    for name, meta in registry.list_all().items():
        print(f" -> [{meta.service_name}] Protocolo: {meta.protocol} | {meta.description}")

    # Carga de chips no estoque físico da operadora
    inventory_svc.add_sim_to_warehouse("8955110099887766554")
    inventory_svc.add_sim_to_warehouse("8955110011223344556")

    # 2. Inicialização do Barramento (ESB)
    esb = TelecomProvisioningESB(registry=registry)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Ativação Regular de Linha 5G (Happy Path)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Pedido de Ativação de Linha Celular Móvel (Orquestração Completa) ---")
    crm_req_1 = {
        "order_id": "ORD_VIVO_99120",
        "subscriber": {
            "full_name": "Juliana Mendes",
            "cpf": "123.456.789-00",
            "email": "juliana@mendes.com",
        },
        "line": {
            "phone_number": "+5511988887777",
            "sim_card_iccid": "8955110099887766554",
            "plan_id": "POS_ILIMITADO_50GB",
            "monthly_price": 129.90,
        },
    }

    res_1 = esb.process_activation(crm_req_1)
    print(f"Status: {res_1.status}")
    print(f"Linha: {res_1.msisdn} | Nó de Antena HLR: {res_1.hlr_routing_code}")
    print(f"Ciclo de Faturamento: Dia {res_1.billing_cycle_day}")
    print(f"Mensagem: {res_1.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Chip Não Cadastrado ou Já Utilizado (Rejeição Rápida)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Tentativa de Ativação com Chip Inexistente no Inventário ---")
    crm_req_chip_invalido = {
        "order_id": "ORD_VIVO_99121",
        "subscriber": {
            "full_name": "Carlos Alencar",
            "cpf": "222.333.444-55",
            "email": "carlos@alencar.com",
        },
        "line": {
            "phone_number": "+5511977776666",
            "sim_card_iccid": "0000000000000000000",  # Chip inexistente
            "plan_id": "CONTROLE_20GB",
            "monthly_price": 59.90,
        },
    }
    res_2 = esb.process_activation(crm_req_chip_invalido)
    print(f"Status: {res_2.status} | Resposta: {res_2.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Falha no Billing com Rollback Compensatório da Rede HLR
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Rejeição no Faturamento com Desprovisionamento de Rede HLR ---")
    crm_req_inadimplente = {
        "order_id": "ORD_VIVO_99122",
        "subscriber": {
            "full_name": "Marcos Inadimplente",
            "cpf": "INADIMPLENTE_9999",
            "email": "marcos@test.com",
        },
        "line": {
            "phone_number": "+5511966665555",
            "sim_card_iccid": "8955110011223344556",  # Chip válido em estoque
            "plan_id": "BLACK_100GB",
            "monthly_price": 299.90,
        },
    }
    res_3 = esb.process_activation(crm_req_inadimplente)
    print(f"Status: {res_3.status}")
    print(f"Mensagem de Compensação: {res_3.message}")

    # Verificação de segurança: Linha não deve estar ativa na rede celular
    check_hlr = hlr_svc.execute_mml_command("DEL-SUB:MSISDN=+5511966665555")
    print(f"Confirmação de que o HLR foi limpo: {check_hlr}")

    print("\n" + "=" * 80)
    print(" Exemplo 02 de Service-Oriented Architecture (SOA) finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
