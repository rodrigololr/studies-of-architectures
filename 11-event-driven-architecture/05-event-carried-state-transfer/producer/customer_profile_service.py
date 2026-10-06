"""Customer Profile Microservice (Master Data Management)."""

import uuid
from typing import Dict, Optional
from broker.event_broker import EventBroker
from events.customer_events import (
    AddressSnapshot,
    CustomerSnapshot,
    CustomerProfileUpdatedEvent,
)


class CustomerProfileService:
    """Microsserviço proprietário dos dados cadastrais dos clientes."""

    def __init__(self, broker: EventBroker) -> None:
        self._broker = broker
        self._customers_db: Dict[str, CustomerSnapshot] = {}
        self._version_counters: Dict[str, int] = {}
        self.is_online: bool = True  # Toggle para simulação de queda total do serviço

    def upsert_customer(
        self,
        customer_id: str,
        name: str,
        tax_id: str,
        email: str,
        tier: str,
        street: str,
        number: str,
        city: str,
        state: str,
        postal_code: str,
    ) -> CustomerProfileUpdatedEvent:
        if not self.is_online:
            raise ConnectionError("CustomerProfileService está OFFLINE.")

        version = self._version_counters.get(customer_id, 0) + 1
        self._version_counters[customer_id] = version

        snapshot = CustomerSnapshot(
            customer_id=customer_id,
            full_name=name,
            tax_id=tax_id,
            email=email,
            tier=tier,
            billing_address=AddressSnapshot(
                street=street,
                number=number,
                city=city,
                state=state,
                postal_code=postal_code,
            ),
        )
        self._customers_db[customer_id] = snapshot

        # Emite evento com o estado completo carreado (ECST)
        event = CustomerProfileUpdatedEvent(
            event_id=f"EVT-CUST-{uuid.uuid4().hex[:8].upper()}",
            sequence_number=version,
            customer=snapshot,
        )
        self._broker.publish("customer.lifecycle.v1", event)
        return event

    def query_remote_rest(self, customer_id: str) -> Optional[CustomerSnapshot]:
        """Simulação de endpoint REST síncrono que falhará se o serviço estiver offline."""
        if not self.is_online:
            raise ConnectionError("Falha de rede (503 Service Unavailable): CustomerProfileService inacessível.")
        return self._customers_db.get(customer_id)
