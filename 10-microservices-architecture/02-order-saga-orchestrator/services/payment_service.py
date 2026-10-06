"""Payment Microservice - Processador de cobranças e estornos."""

import uuid
from typing import Dict, Any, Tuple


class PaymentService:
    """Microsserviço de Pagamentos com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._payments_db: Dict[str, Dict[str, Any]] = {}
        # Clientes com limite de crédito simulado
        self._customer_credit_limits: Dict[str, float] = {
            "CUST-ALICE": 15000.0,
            "CUST-BOB": 50.0,       # Limite insuficiente
            "CUST-CAROL": 15000.0,
            "CUST-DANIEL": 15000.0,
        }

    def process_charge(
        self, order_id: str, customer_id: str, amount: float
    ) -> Tuple[bool, str]:
        """Etapa direta (Forward step)."""
        limit = self._customer_credit_limits.get(customer_id, 1000.0)
        if amount > limit:
            return False, f"Crédito insuficiente (Limite: R$ {limit:.2f}, Solicitado: R$ {amount:.2f})"

        payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        self._payments_db[payment_id] = {
            "payment_id": payment_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "status": "CAPTURED",
        }
        # Deduz limite
        self._customer_credit_limits[customer_id] -= amount
        return True, payment_id

    def refund_payment(self, payment_id: str) -> bool:
        """Ação Compensatória da Saga (Compensating transaction)."""
        if payment_id in self._payments_db:
            record = self._payments_db[payment_id]
            if record["status"] == "CAPTURED":
                record["status"] = "REFUNDED"
                # Estorna limite
                self._customer_credit_limits[record["customer_id"]] += record["amount"]
                return True
        return False
