"""Serviço Interno de ERP e Armazenagem (WMS / SAP S/4HANA Simulator)."""

import uuid
from typing import Dict, Any, List
from canonical.supply_chain_models import CanonicalDespatchAdvice


class WarehouseErpService:
    """Core ERP da montadora automobilística."""

    def __init__(self) -> None:
        # Armazéns por categoria de peça
        # Linha Powertrain (Motores / Injeção) -> Armazém Central "W-POWERTRAIN-01"
        # Linha Chassis / Freios -> Armazém "W-CHASSIS-02"
        # Linha Elétrica -> Armazém "W-ELECTRO-03"
        self._received_shipments: Dict[str, Dict[str, Any]] = {}

    def book_advanced_shipping_notice(
        self, asn: CanonicalDespatchAdvice, target_warehouse: str
    ) -> str:
        """Registra a entrada contábil e de armazém no ERP."""
        receipt_id = f"MIGO-{uuid.uuid4().hex[:8].upper()}"
        self._received_shipments[receipt_id] = {
            "document_id": asn.document_id,
            "warehouse": target_warehouse,
            "supplier": asn.supplier_code,
            "items_count": len(asn.items),
            "total_units": sum(item.quantity for item in asn.items),
        }
        return receipt_id

    def get_shipment(self, receipt_id: str) -> Dict[str, Any]:
        return self._received_shipments.get(receipt_id, {})
