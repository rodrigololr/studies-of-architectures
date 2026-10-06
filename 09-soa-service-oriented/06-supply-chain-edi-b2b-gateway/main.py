"""Demonstração de SOA: Gateway B2B de Cadeia de Suprimentos (EDIFACT DESADV para ERP).

Cenários demonstrados:
1. Ingestão e roteamento de remessa de injetores (Bosch -> Armazém Powertrain W-POWERTRAIN-01)
2. Ingestão e roteamento de remessa de freios (Brembo -> Armazém Chassis W-CHASSIS-02)
3. Rejeição de EDIFACT corrompido com erro de paridade de segmentos e desvio para DLQ
4. Verificação de estoque no ERP corporativo e auditoria da Dead-Letter Queue
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from erp_core.warehouse_erp_service import WarehouseErpService
from esb.edi_b2b_gateway import EdiB2BGatewayBus


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Barramento SOA de Integração B2B / EDIFACT com ERP...")

    erp = WarehouseErpService()
    gateway = EdiB2BGatewayBus(erp_service=erp)

    # -------------------------------------------------------------------------
    # Cenário 1: Remessa Bosch - Injetores (Powertrain)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Mensagem UN/EDIFACT DESADV da Bosch (Injetores de Combustível)")
    # 7 segmentos no total: UNH, BGM, DTM, NAD, NAD, LIN, QTY, UNT -> UNT declara 8
    edifact_bosch = (
        "UNH+1+DESADV:D:01B:UN:EAN007'"
        "BGM+351+DN-BOSCH-88491+9'"
        "DTM+137:20261006:102'"
        "NAD+BY+OEM-VOLKSWAGEN'"
        "NAD+SE+BOSCH-BRAZIL'"
        "LIN+1++INJ-9921-DIESEL:IN'"
        "QTY+12:600:PCE'"
        "UNT+8+1'"
    )
    print(f"Payload EDIFACT Recebido:\n  {edifact_bosch}")
    res1 = gateway.ingest_edifact_desadv(edifact_bosch)
    print(f"\nResultado da Mediação do Barramento:")
    print(f"  Sucesso: {res1.is_success}")
    print(f"  ID do Documento: {res1.document_id}")
    print(f"  Roteamento para Armazém: {res1.assigned_warehouse}")
    print(f"  Protocolo de Recebimento no ERP: {res1.erp_receipt_id}")
    print(f"  Confirmação B2B (CONTRL ACK):\n    {res1.edifact_acknowledgement}")
    assert res1.is_success is True
    assert res1.assigned_warehouse == "W-POWERTRAIN-01"
    assert res1.erp_receipt_id is not None

    # -------------------------------------------------------------------------
    # Cenário 2: Remessa Brembo - Pinças de Freio (Chassis)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Mensagem UN/EDIFACT DESADV da Brembo (Pinças de Freio)")
    edifact_brembo = (
        "UNH+2+DESADV:D:01B:UN:EAN007'"
        "BGM+351+DN-BREMBO-44102+9'"
        "DTM+137:20261006:102'"
        "NAD+BY+OEM-VOLKSWAGEN'"
        "NAD+SE+BREMBO-ITALY'"
        "LIN+1++BRK-4002-CERAMIC:IN'"
        "QTY+12:120:PCE'"
        "UNT+8+2'"
    )
    res2 = gateway.ingest_edifact_desadv(edifact_brembo)
    print(f"Resultado da Mediação do Barramento:")
    print(f"  Sucesso: {res2.is_success}")
    print(f"  Roteamento para Armazém: {res2.assigned_warehouse}")
    print(f"  Protocolo de Recebimento no ERP: {res2.erp_receipt_id}")
    assert res2.is_success is True
    assert res2.assigned_warehouse == "W-CHASSIS-02"

    # -------------------------------------------------------------------------
    # Cenário 3: Mensagem Corrompida / Erro de Paridade de Segmentos (DLQ)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: EDIFACT com Violação de Integridade (Desvio para Dead-Letter Queue)")
    # Possui 8 segmentos mas declara UNT+15+3 (erro de contagem)
    edifact_corrupted = (
        "UNH+3+DESADV:D:01B:UN:EAN007'"
        "BGM+351+DN-CORRUPTED-000+9'"
        "DTM+137:20261006:102'"
        "NAD+BY+OEM-VOLKSWAGEN'"
        "NAD+SE+UNKNOWN-VENDOR'"
        "LIN+1++GEN-001:IN'"
        "QTY+12:50:PCE'"
        "UNT+15+3'"
    )
    res3 = gateway.ingest_edifact_desadv(edifact_corrupted)
    print(f"Resultado da Mediação do Barramento:")
    print(f"  Sucesso: {res3.is_success}")
    print(f"  Erro Capturado: {res3.error_message}")
    print(f"  Resposta EDIFACT (APERAK NACK):\n    {res3.edifact_acknowledgement}")
    assert res3.is_success is False
    assert len(gateway.dlq_entries) == 1
    assert "Contagem de segmentos inválida" in gateway.dlq_entries[0].reason

    # -------------------------------------------------------------------------
    # Cenário 4: Auditoria do ERP e da Fila de Mensagens Mortas (DLQ)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Conferência dos Dados Registrados no ERP Core")
    rec1 = erp.get_shipment(res1.erp_receipt_id)
    print(f"Registro ERP Remessa 1 (Bosch): {rec1}")
    rec2 = erp.get_shipment(res2.erp_receipt_id)
    print(f"Registro ERP Remessa 2 (Brembo): {rec2}")
    print(f"Entradas na Dead-Letter Queue (DLQ): {len(gateway.dlq_entries)}")
    for i, entry in enumerate(gateway.dlq_entries, 1):
        print(f"  - DLQ #{i} | Motivo: {entry.reason}")

    print_separator("Todos os cenários do Gateway B2B / EDIFACT foram validados com sucesso!")


if __name__ == "__main__":
    main()
