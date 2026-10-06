"""Serviço Corporativo: Emissão Oficial de Bilhete Eletrônico (IATA E-Ticket Service)."""

import random
from typing import Dict, Any


class ETicketIssuanceService:
    """Serviço responsável por gerar o bilhete eletrônico de 13 dígitos IATA."""
    def issue_eticket(self, issue_payload: Dict[str, Any]) -> Dict[str, Any]:
        pnr = issue_payload.get("pnr_code")
        pax_name = issue_payload.get("passenger_name")
        airline_iata_prefix = "957"  # Prefixo IATA da LATAM/Parceira
        random_suffix = "".join(str(random.randint(0, 9)) for _ in range(10))
        eticket_number = f"{airline_iata_prefix}-{random_suffix}"

        return {
            "pnr": pnr,
            "passenger": pax_name,
            "eticket_number": eticket_number,
            "status": "ISSUED",
        }
