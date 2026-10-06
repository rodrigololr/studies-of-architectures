"""Enterprise Service Bus (ESB) Orchestrator: Coordenação do Macroprocesso de Emissão Aérea."""

from typing import Dict, Any
from canonical.flight_models import (
    CanonicalReservationRequest,
    CanonicalReservationResponse,
)
from esb.service_registry import ServiceRegistry
from esb.message_transformer import MessageTransformer
from services.legacy_gds_service import LegacyGdsService
from services.payment_service import CorporatePaymentService
from services.eticket_service import ETicketIssuanceService


class AirlineEnterpriseServiceBus:
    """O Barramento Central de Serviços Corporativos (ESB).
    
    Aplica:
    1. Descoberta dinâmica de serviços via Service Registry.
    2. Transformação de protocolos e Canonical Data Model (CDM).
    3. Orquestração de negócio e compensação de falhas em serviços legados.
    """

    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry
        self._transformer = MessageTransformer()

    def process_booking_request(self, raw_web_request: Dict[str, Any]) -> CanonicalReservationResponse:
        # 1. Validação de disponibilidade de serviços no Service Registry (Discoverability)
        gds_meta = self._registry.lookup("LegacyGdsService")
        payment_meta = self._registry.lookup("CorporatePaymentService")
        eticket_meta = self._registry.lookup("ETicketIssuanceService")

        if not gds_meta or not payment_meta or not eticket_meta:
            return CanonicalReservationResponse(
                pnr_code=None,
                eticket_number=None,
                status="ESB_SERVICE_UNAVAILABLE",
                authorization_code=None,
                message="Falha no ESB: Um ou mais serviços corporativos participantes não estão registrados.",
            )

        gds: LegacyGdsService = gds_meta.service_instance
        payment_svc: CorporatePaymentService = payment_meta.service_instance
        eticket_svc: ETicketIssuanceService = eticket_meta.service_instance

        # 2. Transformação do protocolo de entrada (JSON/REST) para o Modelo Canônico (CDM)
        canonical_req = self._transformer.web_json_to_canonical(raw_web_request)

        # 3. Mediação com Legado: Tradução CDM -> Comando TTY GDS e bloqueio de assento
        gds_cmd = self._transformer.canonical_to_gds_tty(canonical_req)
        gds_raw_resp = gds.execute_terminal_command(gds_cmd)
        ok, pnr = self._transformer.parse_gds_response(gds_raw_resp)

        if not ok or not pnr:
            return CanonicalReservationResponse(
                pnr_code=None,
                eticket_number=None,
                status="GDS_REJECTED",
                authorization_code=None,
                message=f"Distribuição aérea GDS recusou retenção de assento. Resposta: {gds_raw_resp}",
            )

        # 4. Invocação do Serviço de Pagamento Financeiro
        payment_payload = self._transformer.canonical_to_payment_payload(canonical_req)
        pay_result = payment_svc.authorize_and_charge(payment_payload)

        # 5. Compensação caso o pagamento falhe: Libera o PNR no GDS
        if not pay_result["success"]:
            # Rollback compensatório no legado
            gds.execute_terminal_command(f"CANCEL|PNR:{pnr}")
            return CanonicalReservationResponse(
                pnr_code=pnr,
                eticket_number=None,
                status="PAYMENT_FAILED",
                authorization_code=None,
                message=f"Pagamento não aprovado ({pay_result['error_reason']}). Reserva {pnr} cancelada no GDS.",
            )

        # 6. Pagamento Aprovado: Emissão do Bilhete Eletrônico IATA
        eticket_payload = self._transformer.canonical_and_pnr_to_eticket_payload(canonical_req, pnr)
        eticket_result = eticket_svc.issue_eticket(eticket_payload)

        # 7. Resposta Canônica Consolidada
        return CanonicalReservationResponse(
            pnr_code=pnr,
            eticket_number=eticket_result["eticket_number"],
            status="CONFIRMED",
            authorization_code=pay_result["auth_code"],
            message=f"Reserva e Bilhete emitidos com sucesso pela malha corporativa SOA.",
        )
