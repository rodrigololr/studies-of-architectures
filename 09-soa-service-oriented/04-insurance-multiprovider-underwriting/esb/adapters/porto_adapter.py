"""Adaptador de Barramento para o Provedor Porto Seguro (SOAP / XML)."""

import xml.etree.ElementTree as ET
from canonical.underwriting_models import (
    CanonicalQuoteRequest,
    QuoteProposal,
    CoverageType,
)
from providers.porto_seguro_provider import PortoSeguroSoapService


class PortoSeguroAdapter:
    def __init__(self, service: PortoSeguroSoapService) -> None:
        self._service = service

    def request_quote(self, request: CanonicalQuoteRequest) -> QuoteProposal:
        # 1. Transformação: CanonicalQuoteRequest -> XML SOAP Payload
        xml_request = (
            f"<PortoQuoteRequest>"
            f"  <VeiculoAno>{request.vehicle.year}</VeiculoAno>"
            f"  <ValorFipe>{request.vehicle.fipe_value_brl:.2f}</ValorFipe>"
            f"  <CondutorIdade>{request.driver.age}</CondutorIdade>"
            f"  <TipoCobertura>{request.coverage.value}</TipoCobertura>"
            f"  <PossuiGaragem>{'true' if request.driver.has_garage else 'false'}</PossuiGaragem>"
            f"</PortoQuoteRequest>"
        )

        # 2. Invocação do Provedor
        xml_response = self._service.quote_policy_soap(xml_request)

        # 3. Transformação: XML Response -> Canonical QuoteProposal
        try:
            root = ET.fromstring(xml_response)
            status = root.findtext(".//Status", "ERRO")
            if status == "APROVADO":
                protocolo = root.findtext(".//Protocolo", "")
                premio = float(root.findtext(".//PremioAnual", "0.0"))
                franquia = float(root.findtext(".//Franquia", "0.0"))
                return QuoteProposal(
                    carrier_name="Porto Seguro",
                    carrier_protocol=protocolo,
                    annual_premium_brl=premio,
                    deductible_brl=franquia,
                    coverage=request.coverage,
                    is_eligible=True,
                )
            else:
                motivo = root.findtext(".//Motivo", "Risco não aceito")
                return QuoteProposal(
                    carrier_name="Porto Seguro",
                    carrier_protocol="",
                    annual_premium_brl=0.0,
                    deductible_brl=0.0,
                    coverage=request.coverage,
                    is_eligible=False,
                    rejection_reason=motivo,
                )
        except Exception as exc:
            return QuoteProposal(
                carrier_name="Porto Seguro",
                carrier_protocol="",
                annual_premium_brl=0.0,
                deductible_brl=0.0,
                coverage=request.coverage,
                is_eligible=False,
                rejection_reason=f"Falha na serialização XML: {exc}",
            )
