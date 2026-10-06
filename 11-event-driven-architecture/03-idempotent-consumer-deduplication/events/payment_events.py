"""Payment Webhook Event Models."""

import time
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class PaymentWebhookEvent:
    event_id: str           # Chave de idempotência única (ex: "evt_pix_991823")
    payment_intent_id: str  # Referência do gateway (ex: "pi_3MtwBwLkd")
    customer_id: str
    amount: float
    currency: str = "BRL"
    event_timestamp: float = field(default_factory=time.time)
