"""Canonical Data Model (CDM) - Modelo de Dados Canônico Corporativo de Aviação.

Este schema canônico é a espinha dorsal de interoperabilidade do ESB. Todos os sistemas
(Web, Mobile, Agências de Viagem, GDS legados) são traduzidos para este contrato padrão.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PassengerInfo:
    first_name: str
    last_name: str
    document_id: str
    email: str


@dataclass(frozen=True)
class FlightSegment:
    flight_number: str       # ex: "LA3301"
    origin_airport: str      # ex: "GRU"
    destination_airport: str # ex: "MIA"
    departure_date: str      # ex: "2026-11-20"
    seat_class: str          # ex: "Y" (Econômica), "J" (Executiva)


@dataclass(frozen=True)
class CanonicalReservationRequest:
    """Contrato Canônico de Solicitação de Reserva de Voo."""
    request_id: str
    passenger: PassengerInfo
    segment: FlightSegment
    payment_card_token: str
    amount_fare: float


@dataclass(frozen=True)
class CanonicalReservationResponse:
    """Contrato Canônico de Resposta da Emissão de Reserva."""
    pnr_code: Optional[str]           # Passenger Name Record (6 caracteres, ex: "KJ89XA")
    eticket_number: Optional[str]     # Bilhete IATA 13 dígitos (ex: "957-2345891204")
    status: str                       # "CONFIRMED", "PAYMENT_FAILED", "GDS_REJECTED"
    authorization_code: Optional[str]
    message: str
