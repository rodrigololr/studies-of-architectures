"""Enterprise Service Bus (ESB): Orquestrador de Transações Bancárias com Mainframe."""

import uuid
from typing import Dict, Any
from canonical.banking_models import (
    AccountIdentification,
    CanonicalTransactionRequest,
    CanonicalTransactionResponse,
)
from esb.copybook_adapter import MainframeCopybookAdapter
from services.currency_exchange_service import ForeignExchangeService
from mainframe_core.mainframe_ledger import MainframeCobolCore


class BankingEnterpriseServiceBus:
    """ESB Bancário responsável por integrar canais modernos com o Mainframe IBM COBOL."""
    def __init__(
        self,
        mainframe: MainframeCobolCore,
        fx_service: ForeignExchangeService,
    ) -> None:
        self._mainframe = mainframe
        self._fx = fx_service
        self._adapter = MainframeCopybookAdapter()

    def process_mobile_transaction(self, mobile_json: Dict[str, Any]) -> CanonicalTransactionResponse:
        tx_id = mobile_json.get("tx_id", f"TX{uuid.uuid4().hex[:8].upper()}")
        currency = mobile_json.get("currency", "BRL").upper()
        raw_amount = float(mobile_json.get("amount", 0.0))

        # 1. Mediação de Câmbio: Se transação for em USD ou EUR, converte para BRL via serviço FX
        if currency != "BRL":
            amount_brl = self._fx.convert_to_brl(raw_amount, currency)
        else:
            amount_brl = raw_amount

        # 2. Construção do Modelo Canônico (CDM)
        canonical_req = CanonicalTransactionRequest(
            transaction_id=tx_id,
            account=AccountIdentification(
                branch_code=mobile_json.get("branch", ""),
                account_number=mobile_json.get("account", ""),
            ),
            transaction_type=mobile_json.get("type", "D"),
            amount_brl=amount_brl,
            original_currency=currency,
        )

        # 3. Serialização para Layout Fixo COBOL (Copybook de 33 bytes)
        copybook_in = self._adapter.encode_request(canonical_req)

        # 4. Invocação do Mainframe Legado CICS
        copybook_out = self._mainframe.process_copybook_transaction(copybook_in)

        # 5. Desserialização do buffer do Mainframe para Resposta Canônica
        return self._adapter.decode_response(tx_id, copybook_out)
