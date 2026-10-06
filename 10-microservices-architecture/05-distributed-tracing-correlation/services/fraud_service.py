"""FraudDetectionService instrumentado com Distributed Tracing."""

import time
from typing import Dict, Any
from tracing.tracer import Tracer


class FraudDetectionService:
    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def evaluate_risk(self, headers: Dict[str, str], amount: float) -> Dict[str, Any]:
        with self._tracer.start_span("evaluate_transaction_risk", headers) as span:
            span.attributes["risk.evaluation_engine"] = "ML-FRAUD-V3"
            span.attributes["transaction.amount"] = amount
            time.sleep(0.01)  # Simula latência de processamento

            if amount > 10000.0:
                raise ValueError("ALERTA DE FRAUDE: Transação suspeita bloqueada pelo motor de risco.")

            return {"is_safe": True, "risk_score": 0.04}
