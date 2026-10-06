"""Enterprise Service Bus (ESB): Orquestrador de Cotação Multi-Seguradoras (Scatter-Gather)."""

from typing import List, Dict, Any
from canonical.underwriting_models import (
    CanonicalQuoteRequest,
    QuoteProposal,
    AggregatedQuoteResult,
)
from esb.adapters.porto_adapter import PortoSeguroAdapter
from esb.adapters.allianz_adapter import AllianzAdapter
from esb.adapters.bradesco_adapter import BradescoAdapter


class InsuranceBrokerESB:
    """Barramento Corporativo de Integração de Seguradoras.
    
    Implementa o padrão EIP 'Scatter-Gather' e 'Content-Based Routing':
    1. Recebe requisição no modelo canônico (CDM).
    2. Realiza fan-out para todos os adaptadores de provedores integrados.
    3. Normaliza as respostas proprietárias para o CDM.
    4. Agrega, compara e elege a proposta mais competitiva.
    """

    def __init__(
        self,
        porto_adapter: PortoSeguroAdapter,
        allianz_adapter: AllianzAdapter,
        bradesco_adapter: BradescoAdapter,
    ) -> None:
        self._porto = porto_adapter
        self._allianz = allianz_adapter
        self._bradesco = bradesco_adapter

    def quote_across_carriers(self, request: CanonicalQuoteRequest) -> AggregatedQuoteResult:
        proposals: List[QuoteProposal] = []
        failed_carriers: List[str] = []

        # 1. Dispersão (Scatter) para as seguradoras parceiras
        adapters = [
            ("Porto Seguro", self._porto),
            ("Allianz", self._allianz),
            ("Bradesco Seguros", self._bradesco),
        ]

        for carrier_name, adapter in adapters:
            try:
                proposal = adapter.request_quote(request)
                if proposal.is_eligible:
                    proposals.append(proposal)
                else:
                    failed_carriers.append(f"{carrier_name}: {proposal.rejection_reason}")
            except Exception as exc:
                failed_carriers.append(f"{carrier_name} (Erro de Barramento): {exc}")

        # 2. Agregação e Seleção da Melhor Oferta (Gather)
        best_carrier = None
        cheapest_premium = None

        if proposals:
            # Ordena por menor valor de prêmio anual
            sorted_proposals = sorted(proposals, key=lambda p: p.annual_premium_brl)
            best_carrier = sorted_proposals[0].carrier_name
            cheapest_premium = sorted_proposals[0].annual_premium_brl

        return AggregatedQuoteResult(
            request_id=request.request_id,
            total_requested=len(adapters),
            successful_proposals=proposals,
            failed_carriers=failed_carriers,
            best_value_carrier=best_carrier,
            cheapest_premium_brl=cheapest_premium,
        )
