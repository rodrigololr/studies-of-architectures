"""Adaptador de Barramento para o Provedor Allianz (REST / JSON)."""

from canonical.underwriting_models import (
    CanonicalQuoteRequest,
    QuoteProposal,
)
from providers.allianz_provider import AllianzRestService


class AllianzAdapter:
    def __init__(self, service: AllianzRestService) -> None:
        self._service = service

    def request_quote(self, request: CanonicalQuoteRequest) -> QuoteProposal:
        # 1. Transformação: CanonicalQuoteRequest -> Allianz JSON Payload
        json_req = {
            "asset": {
                "manufacturing_year": request.vehicle.year,
                "model_description": f"{request.vehicle.make} {request.vehicle.model}",
                "market_valuation": request.vehicle.fipe_value_brl,
            },
            "risk_profile": {
                "driver_age": request.driver.age,
                "driving_experience_years": request.driver.license_years,
            },
            "selected_tier": request.coverage.value,
        }

        # 2. Invocação do Provedor
        json_res = self._service.quote_policy_rest(json_req)

        # 3. Transformação: JSON Response -> Canonical QuoteProposal
        outcome = json_res.get("outcome", "UNKNOWN")
        if outcome == "ACCEPTED":
            costs = json_res.get("cost_breakdown", {})
            return QuoteProposal(
                carrier_name="Allianz",
                carrier_protocol=json_res.get("quote_reference", ""),
                annual_premium_brl=float(costs.get("annual_premium", 0.0)),
                deductible_brl=float(costs.get("deductible_amount", 0.0)),
                coverage=request.coverage,
                is_eligible=True,
            )
        else:
            return QuoteProposal(
                carrier_name="Allianz",
                carrier_protocol="",
                annual_premium_brl=0.0,
                deductible_brl=0.0,
                coverage=request.coverage,
                is_eligible=False,
                rejection_reason=json_res.get("decline_reason", "Risco declinado pela seguradora"),
            )
