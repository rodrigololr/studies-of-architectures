"""Adaptador de Barramento para o Provedor Bradesco Seguros (RPC Pipe-Delimited)."""

from canonical.underwriting_models import (
    CanonicalQuoteRequest,
    QuoteProposal,
)
from providers.bradesco_provider import BradescoRpcService


class BradescoAdapter:
    def __init__(self, service: BradescoRpcService) -> None:
        self._service = service

    def request_quote(self, request: CanonicalQuoteRequest) -> QuoteProposal:
        # 1. Transformação: CanonicalQuoteRequest -> String Delimitada
        pipe_req = (
            f"OP:QUOTE|"
            f"VALOR:{request.vehicle.fipe_value_brl:.2f}|"
            f"ANO:{request.vehicle.year}|"
            f"COBERTURA:{request.coverage.value}|"
            f"IDADE:{request.driver.age}"
        )

        # 2. Invocação do Provedor
        pipe_res = self._service.quote_policy_rpc(pipe_req)

        # 3. Transformação: Resposta Delimitada -> Canonical QuoteProposal
        fields = {}
        for part in pipe_res.split("|"):
            if ":" in part:
                k, v = part.split(":", 1)
                fields[k.strip().upper()] = v.strip()

        status = fields.get("STATUS", "ERRO")
        if status == "APROVADO":
            return QuoteProposal(
                carrier_name="Bradesco Seguros",
                carrier_protocol=fields.get("PROTOCOLO", ""),
                annual_premium_brl=float(fields.get("PREMIO", "0.0")),
                deductible_brl=float(fields.get("FRANQUIA", "0.0")),
                coverage=request.coverage,
                is_eligible=True,
            )
        else:
            return QuoteProposal(
                carrier_name="Bradesco Seguros",
                carrier_protocol="",
                annual_premium_brl=0.0,
                deductible_brl=0.0,
                coverage=request.coverage,
                is_eligible=False,
                rejection_reason=fields.get("MOTIVO", "Risco não elegível no Bradesco"),
            )
