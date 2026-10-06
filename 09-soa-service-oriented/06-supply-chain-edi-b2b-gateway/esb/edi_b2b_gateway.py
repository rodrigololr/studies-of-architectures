"""Enterprise Service Bus (ESB): Gateway B2B EDIFACT com Roteamento Baseado em Conteúdo."""

from typing import List, Dict, Any, Optional
from canonical.supply_chain_models import (
    CanonicalDespatchAdvice,
    IngestionResult,
)
from erp_core.warehouse_erp_service import WarehouseErpService
from esb.edifact_parser import EdifactDesadvParser, EdifactSyntaxError


class DeadLetterQueueEntry:
    def __init__(self, raw_payload: str, reason: str) -> None:
        self.raw_payload = raw_payload
        self.reason = reason


class EdiB2BGatewayBus:
    """Barramento de integração B2B que media parceiros de cadeia de suprimentos e o ERP interno."""

    def __init__(self, erp_service: WarehouseErpService) -> None:
        self._erp = erp_service
        self._parser = EdifactDesadvParser()
        self._dead_letter_queue: List[DeadLetterQueueEntry] = []

    def ingest_edifact_desadv(self, raw_edifact: str) -> IngestionResult:
        # 1. Transformação de Protocolo/Mensagem: EDIFACT -> CDM
        try:
            canonical_asn = self._parser.parse(raw_edifact)
        except EdifactSyntaxError as exc:
            # Envia para Dead-Letter Queue (DLQ) para análise de operadores B2B
            self._dead_letter_queue.append(DeadLetterQueueEntry(raw_edifact, str(exc)))
            ack_rejection = self._parser.generate_acknowledgement(
                doc_id="UNKNOWN", is_accepted=False, error_msg=str(exc)
            )
            return IngestionResult(
                is_success=False,
                document_id="REJECTED",
                assigned_warehouse=None,
                erp_receipt_id=None,
                error_message=str(exc),
                edifact_acknowledgement=ack_rejection,
            )

        # 2. Content-Based Routing (Roteamento baseado em conteúdo das peças)
        target_warehouse = self._determine_warehouse(canonical_asn)

        # 3. Invocação do Core ERP Corporativo
        receipt_id = self._erp.book_advanced_shipping_notice(canonical_asn, target_warehouse)

        # 4. Geração de Confirmação B2B (EDIFACT CONTRL ACK)
        ack_success = self._parser.generate_acknowledgement(
            doc_id=canonical_asn.document_id, is_accepted=True
        )

        return IngestionResult(
            is_success=True,
            document_id=canonical_asn.document_id,
            assigned_warehouse=target_warehouse,
            erp_receipt_id=receipt_id,
            edifact_acknowledgement=ack_success,
        )

    def _determine_warehouse(self, asn: CanonicalDespatchAdvice) -> str:
        """Roteador baseado em conteúdo: avalia prefixo dos itens expedidos."""
        for item in asn.items:
            part = item.part_number.upper()
            if part.startswith("INJ-") or "ENG" in part:
                return "W-POWERTRAIN-01"
            elif part.startswith("BRK-") or "CHAS" in part:
                return "W-CHASSIS-02"
        return "W-GENERAL-00"

    @property
    def dlq_entries(self) -> List[DeadLetterQueueEntry]:
        return list(self._dead_letter_queue)
