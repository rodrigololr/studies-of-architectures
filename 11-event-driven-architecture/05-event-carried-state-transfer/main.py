"""Demonstração de EDA: Event-Carried State Transfer (ECST) e Autonomia de Consumidores.

Cenários demonstrados:
1. Cadastro inicial do cliente: Emissão de evento ECST contendo o snapshot completo da entidade
2. Atualização de projeções locais nos microsserviços de Faturamento (Invoicing) e Logística (Shipping)
3. Operação com zero saltos de rede remota (Zero Remote REST calls)
4. Atualização de endereço do cliente e sincronização assíncrona dos caches locais
5. Queda total do serviço mestre (503 Service Unavailable): Consumidores continuam faturando e despachando com autonomia absoluta
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from broker.event_broker import EventBroker
from producer.customer_profile_service import CustomerProfileService
from consumers.invoicing_service import InvoicingService
from consumers.shipping_service import ShippingService


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Ecossistema Orientado a Eventos com Padrão ECST...")

    # 1. Barramento de Mensageria
    broker = EventBroker()

    # 2. Produtor Mestre (Customer Profile Service)
    customer_svc = CustomerProfileService(broker)

    # 3. Consumidores Autônomos (Invoicing e Shipping)
    invoicing_svc = InvoicingService()
    shipping_svc = ShippingService()

    # Inscrição dos consumidores no tópico de ciclo de vida do cliente
    broker.subscribe("customer.lifecycle.v1", invoicing_svc.handle_customer_event)
    broker.subscribe("customer.lifecycle.v1", shipping_svc.handle_customer_event)

    # -------------------------------------------------------------------------
    # Cenário 1: Cadastro Inicial e Broadcast ECST (Snapshot Completo)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Cadastro Inicial do Cliente com Envio do Snapshot Completo (ECST)")
    ev1 = customer_svc.upsert_customer(
        customer_id="CUST-100",
        name="TechSolutions Consultoria Ltda",
        tax_id="12.345.678/0001-90",
        email="financeiro@techsolutions.com",
        tier="GOLD",
        street="Rua Barão de Jaguara",
        number="500",
        city="Campinas",
        state="SP",
        postal_code="13015-002",
    )
    print(f"Evento Emitido: CustomerProfileUpdatedEvent [Seq: {ev1.sequence_number}]")
    print(f"Snapshot Carreado no Evento: {ev1.customer.full_name} | CNPJ: {ev1.customer.tax_id} | Cidade: {ev1.customer.billing_address.city}")
    print(f"  - Invoicing Service recebeu e populou projeção local? {'CUST-100' in invoicing_svc._local_customer_projection}")
    print(f"  - Shipping Service recebeu e populou projeção local? {'CUST-100' in shipping_svc._local_address_projection}")
    assert "CUST-100" in invoicing_svc._local_customer_projection
    assert "CUST-100" in shipping_svc._local_address_projection

    # -------------------------------------------------------------------------
    # Cenário 2: Operações Autônomas Locais (Zero Chamadas REST)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Emissão de Nota Fiscal e Despacho de Mercadoria com Projeção Local")
    inv1 = invoicing_svc.issue_tax_invoice("ORD-001", "CUST-100", 12500.0)
    ship1 = shipping_svc.dispatch_order("ORD-001", "CUST-100")
    print(f"Nota Fiscal Gerada: {inv1['invoice_number']} | Razão Social: {inv1['recipient_legal_name']} | Fonte: {inv1['data_source']}")
    print(f"Envio Despachado:   {ship1['tracking_code']} | Destino: {ship1['destination_city']}/{ship1['destination_state']} (CEP: {ship1['destination_zip']})")
    assert inv1["recipient_legal_name"] == "TechSolutions Consultoria Ltda"
    assert ship1["destination_city"] == "Campinas"

    # -------------------------------------------------------------------------
    # Cenário 3: Atualização de Endereço e Sincronização Assíncrona
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Mudança de Endereço (Campinas -> São Paulo) e Re-emissão de ECST")
    ev2 = customer_svc.upsert_customer(
        customer_id="CUST-100",
        name="TechSolutions Consultoria Ltda",
        tax_id="12.345.678/0001-90",
        email="financeiro@techsolutions.com",
        tier="PLATINUM",
        street="Avenida Paulista",
        number="1000",
        city="São Paulo",
        state="SP",
        postal_code="01310-100",
    )
    print(f"Evento Atualizado Emitido: Versão {ev2.sequence_number}")
    inv2 = invoicing_svc.issue_tax_invoice("ORD-002", "CUST-100", 3500.0)
    ship2 = shipping_svc.dispatch_order("ORD-002", "CUST-100")
    print(f"Novo Endereço de Entrega refletido localmente: {ship2['destination_city']} - CEP: {ship2['destination_zip']}")
    assert ship2["destination_city"] == "São Paulo"
    assert ship2["destination_zip"] == "01310-100"

    # -------------------------------------------------------------------------
    # Cenário 4: Queda Total do Microsserviço Mestre (Autonomia Radical)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Queda do Serviço Mestre de Cadastro (503 Service Unavailable)")
    customer_svc.is_online = False
    print("ALERTA: CustomerProfileService caiu e está totalmente INACESSÍVEL.")

    # Tentativa de chamada REST síncrona direta falha!
    try:
        customer_svc.query_remote_rest("CUST-100")
        assert False, "Deveria ter falhado com ConnectionError"
    except ConnectionError as exc:
        print(f"Chamada síncrona REST falhou como esperado: {exc}")

    # No entanto, os serviços com ECST continuam operando normalmente sem nenhuma degradação!
    inv3 = invoicing_svc.issue_tax_invoice("ORD-003", "CUST-100", 8900.0)
    ship3 = shipping_svc.dispatch_order("ORD-003", "CUST-100")
    print("\nOperações executadas com sucesso pelos serviços autônomos durante a queda do mestre:")
    print(f"  -> Nota Fiscal emitida com sucesso: {inv3['invoice_number']} para {inv3['recipient_legal_name']}")
    print(f"  -> Pacote despachado com sucesso:   {ship3['tracking_code']} para {ship3['destination_city']}")
    assert inv3["recipient_legal_name"] == "TechSolutions Consultoria Ltda"
    assert ship3["destination_city"] == "São Paulo"

    print_separator("Todos os cenários do Padrão ECST foram validados com sucesso!")


if __name__ == "__main__":
    main()
