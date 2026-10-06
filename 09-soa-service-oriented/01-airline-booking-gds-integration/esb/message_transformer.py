"""Message Transformer: Tradução de Protocolos e Mapeamento para o Canonical Data Model (CDM)."""

import uuid
from typing import Dict, Any, Tuple
from canonical.flight_models import (
    PassengerInfo,
    FlightSegment,
    CanonicalReservationRequest,
    CanonicalReservationResponse,
)


class MessageTransformer:
    """Componente do ESB responsável por desacoplar protocolos e formatos proprietários."""

    @staticmethod
    def web_json_to_canonical(web_json: Dict[str, Any]) -> CanonicalReservationRequest:
        """Converte JSON/REST da camada Web para o Modelo de Dados Canônico corporativo."""
        req_id = web_json.get("request_id", f"REQ_{uuid.uuid4().hex[:8].upper()}")
        pax_data = web_json.get("passenger", {})
        seg_data = web_json.get("flight", {})

        passenger = PassengerInfo(
            first_name=pax_data.get("first_name", ""),
            last_name=pax_data.get("last_name", ""),
            document_id=pax_data.get("passport_or_cpf", ""),
            email=pax_data.get("email", ""),
        )

        segment = FlightSegment(
            flight_number=seg_data.get("flight_number", ""),
            origin_airport=seg_data.get("origin", ""),
            destination_airport=seg_data.get("destination", ""),
            departure_date=seg_data.get("departure_date", ""),
            seat_class=seg_data.get("cabin_class", "Y"),
        )

        return CanonicalReservationRequest(
            request_id=req_id,
            passenger=passenger,
            segment=segment,
            payment_card_token=web_json.get("card_token", ""),
            amount_fare=float(web_json.get("fare_amount", 0.0)),
        )

    @staticmethod
    def canonical_to_gds_tty(req: CanonicalReservationRequest) -> str:
        """Converte o CDM Canônico para comando de terminal legado do GDS Amadeus/Sabre."""
        # Formato esperado pelo legado: HOLD|FLT:<num>|DATE:<date>|PAX:<last>/<first>
        pax_formatted = f"{req.passenger.last_name.upper()}/{req.passenger.first_name.upper()}"
        return f"HOLD|FLT:{req.segment.flight_number}|DATE:{req.segment.departure_date}|PAX:{pax_formatted}"

    @staticmethod
    def parse_gds_response(raw_resp: str) -> Tuple[bool, str]:
        """Interpreta resposta do terminal GDS e extrai o PNR."""
        # Ex: "RESP:OK|PNR:KJ89XA|STATUS:HOLD_CONFIRMED|TTL:15MIN"
        if not raw_resp.startswith("RESP:OK|"):
            return False, ""
        parts = dict(p.split(":") for p in raw_resp.split("|") if ":" in p)
        return True, parts.get("PNR", "")

    @staticmethod
    def canonical_to_payment_payload(req: CanonicalReservationRequest) -> Dict[str, Any]:
        """Mapeia requisição canônica para contrato de cobrança do Gateway Financeiro."""
        return {
            "card_token": req.payment_card_token,
            "amount": req.amount_fare,
            "customer_doc": req.passenger.document_id,
        }

    @staticmethod
    def canonical_and_pnr_to_eticket_payload(req: CanonicalReservationRequest, pnr: str) -> Dict[str, Any]:
        """Mapeia dados canônicos para emissão do bilhete IATA."""
        return {
            "pnr_code": pnr,
            "passenger_name": f"{req.passenger.first_name} {req.passenger.last_name}",
            "route": f"{req.segment.origin_airport}-{req.segment.destination_airport}",
        }
