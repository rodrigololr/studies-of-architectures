"""Shipping Microservice com projeção local via ECST."""

import uuid
from typing import Dict, Any, List
from events.customer_events import CustomerProfileUpdatedEvent, AddressSnapshot


class ShippingService:
    """Microsserviço de Logística e Frete que utiliza projeção de endereços local."""

    def __init__(self) -> None:
        self._local_address_projection: Dict[str, AddressSnapshot] = {}
        self.dispatched_shipments: List[Dict[str, Any]] = []

    def handle_customer_event(self, event: CustomerProfileUpdatedEvent) -> None:
        """Atualiza o cache local de endereços."""
        self._local_address_projection[event.customer.customer_id] = event.customer.billing_address

    def dispatch_order(self, order_id: str, customer_id: str) -> Dict[str, Any]:
        """Calcula frete e despacha mercadoria consultando estritamente a projeção local."""
        addr = self._local_address_projection.get(customer_id)
        if not addr:
            raise KeyError(f"Endereço para o cliente {customer_id} ausente na projeção de logística.")

        tracking_code = f"TRACK-{uuid.uuid4().hex[:8].upper()}"
        shipment = {
            "tracking_code": tracking_code,
            "order_id": order_id,
            "destination_zip": addr.postal_code,
            "destination_city": addr.city,
            "destination_state": addr.state,
            "data_source": "LOCAL_PROJECTION_CACHE",
        }
        self.dispatched_shipments.append(shipment)
        return shipment
