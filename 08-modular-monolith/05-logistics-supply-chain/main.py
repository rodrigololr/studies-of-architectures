"""Ponto de Entrada e Demonstração Executável - Exemplo 05: Logistics Supply Chain.

Demonstra:
1. Módulos com Bounded Contexts em monólito: Procurement, Warehousing, Transportation, Invoicing.
2. Integração reativa via In-Process Event Bus:
   - Recebimento de compra gera estoque físico no armazém.
   - Expedição de transporte dispara emissão de Nota Fiscal Eletrônica (NF-e).
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.procurement import (
    ProcurementModule,
    CreatePurchaseOrderCommand,
    PurchaseOrderItemDto,
)
from modules.warehousing import WarehousingModule
from modules.transportation import (
    TransportationModule,
    DispatchShipmentCommand,
)
from modules.invoicing import InvoicingModule


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 05: LOGISTICS & SUPPLY CHAIN INTEGRATION")
    print("=" * 80)

    # 1. Composição de Módulos e Barramento Intra-Processo
    event_bus = InProcessEventBus()

    procurement = ProcurementModule(event_bus=event_bus)
    warehousing = WarehousingModule(event_bus=event_bus)
    invoicing = InvoicingModule(event_bus=event_bus)
    transportation = TransportationModule(
        warehousing_module=warehousing,
        event_bus=event_bus,
    )

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Emissão e Recebimento de Pedido de Compra (Procurement -> Warehousing)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Pedido de Compras e Recebimento Físico no Armazém ---")
    po = procurement.create_order(CreatePurchaseOrderCommand(
        supplier_name="WEG Motores Elétricos S/A",
        items=[
            PurchaseOrderItemDto(
                item_code="ENG-IND-200",
                description="Motor Trifásico 200HP Industrial",
                quantity=50,
                unit_cost=3_500.0,
            )
        ],
    ))
    print(f"Ordem de Compra Criada: #{po.po_number} | Fornecedor: {po.supplier_name} | Total: R$ {po.total_cost:,.2f}")

    print("\nCaminhão do fornecedor chega à doca de descarga...")
    po_recebido = procurement.receive_order(po.po_number)
    print(f"Status PO atualizado: {po_recebido.status}")

    # Verifica se o Módulo Warehousing deu entrada no estoque reativamente
    stock_weg = warehousing.get_stock("ENG-IND-200")
    print(f"Verificação de Estoque no Armazém: Item '{stock_weg.item_code}' -> Local: {stock_weg.aisle_location} | Saldo: {stock_weg.available_quantity} un.")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Expedição de Transporte e Separação (Transportation -> Warehousing)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Expedição de Carga para Cliente (Embraer) ---")
    shipment = transportation.dispatch(DispatchShipmentCommand(
        client_name="Embraer Defesa & Segurança",
        destination_city="São José dos Campos - SP",
        truck_plate="BRA2E19",
        item_code="ENG-IND-200",
        quantity=20,
        cargo_value=120_000.0,
    ))
    print(f"Carga Despachada: #{shipment.shipment_id} para {shipment.client_name} (Placa: {shipment.truck_plate})")
    
    # Saldo pós-expedição
    stock_pos = warehousing.get_stock("ENG-IND-200")
    print(f"Saldo remanescente no armazém após expedição: {stock_pos.available_quantity} un (50 iniciais - 20 expedidos)")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Emissão Fiscal Automática (Invoicing reage ao Transporte)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Emissão Fiscal Automática de NF-e (Módulo Invoicing) ---")
    nfe = invoicing.get_by_shipment(shipment.shipment_id)
    if nfe:
        print(f"NF-e Emitida com Sucesso: Chave #{nfe.nfe_key}")
        print(f" -> Destinatário: {nfe.client_name}")
        print(f" -> Valor da Mercadoria: R$ {nfe.total_cargo_value:,.2f}")
        print(f" -> ICMS Destacado (18%): R$ {nfe.icms_tax:,.2f}")
        print(f" -> IPI Destacado (5%): R$ {nfe.ipi_tax:,.2f}")
        print(f" -> Valor Total da NF-e: R$ {nfe.total_invoice_amount:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Tentativa de Expedição com Saldo Insuficiente
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Bloqueio por Falta de Saldo Físico no Armazém ---")
    try:
        # Restam 30 unidades; cliente tenta despachar 40 unidades
        transportation.dispatch(DispatchShipmentCommand(
            client_name="Petrobras Logística",
            destination_city="Santos - SP",
            truck_plate="SPO9K88",
            item_code="ENG-IND-200",
            quantity=40,
            cargo_value=240_000.0,
        ))
    except ValueError as e:
        print(f"Expedição bloqueada com segurança: {e}")

    print("\n" + "=" * 80)
    print(" Exemplo 05 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
