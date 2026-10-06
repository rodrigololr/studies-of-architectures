"""Delivery Microservice - Agendamento e despacho de transportadoras."""

import uuid
from typing import Dict, Any, Tuple


class DeliveryService:
    """Microsserviço de Logística e Entrega com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._dispatches_db: Dict[str, Dict[str, Any]] = {}
        # Lista de CEPs com restrição temporária de entrega
        self._blocked_postal_codes = {"99999-999"}

    def schedule_delivery(
        self, order_id: str, postal_code: str
    ) -> Tuple[bool, str]:
        """Etapa direta: agenda transportadora."""
        if postal_code in self._blocked_postal_codes:
            return False, f"Área de entrega com restrição temporária (CEP: {postal_code})"

        dispatch_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        self._dispatches_db[dispatch_id] = {
            "dispatch_id": dispatch_id,
            "order_id": order_id,
            "postal_code": postal_code,
            "status": "SCHEDULED",
        }
        return True, dispatch_id

    def cancel_delivery(self, dispatch_id: str) -> bool:
        """Ação Compensatória da Saga: Cancela a coleta da transportadora."""
        if dispatch_id in self._dispatches_db:
            self._dispatches_db[dispatch_id]["status"] = "CANCELLED"
            return True
        return False
