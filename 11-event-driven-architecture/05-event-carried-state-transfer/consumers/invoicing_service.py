"""Invoicing Microservice com projeção local via ECST."""

import uuid
from typing import Dict, Any, List, Optional
from events.customer_events import CustomerProfileUpdatedEvent, CustomerSnapshot


class InvoicingService:
    """Microsserviço de Faturamento que gera Notas Fiscais usando projeção local."""

    def __init__(self) -> None:
        # Cache de projeção local denormalizado
        self._local_customer_projection: Dict[str, CustomerSnapshot] = {}
        self.issued_invoices: List[Dict[str, Any]] = []

    def handle_customer_event(self, event: CustomerProfileUpdatedEvent) -> None:
        """Atualiza a projeção local ao receber o snapshot no evento."""
        self._local_customer_projection[event.customer.customer_id] = event.customer

    def issue_tax_invoice(self, order_id: str, customer_id: str, amount: float) -> Dict[str, Any]:
        """Gera nota fiscal usando 100% dados locais sem fazer nenhuma chamada REST externa."""
        customer = self._local_customer_projection.get(customer_id)
        if not customer:
            raise KeyError(f"Cliente {customer_id} não encontrado na projeção local de faturamento.")

        nfe_number = f"NFE-{uuid.uuid4().hex[:8].upper()}"
        invoice = {
            "invoice_number": nfe_number,
            "order_id": order_id,
            "recipient_legal_name": customer.full_name,
            "recipient_tax_id": customer.tax_id,
            "tax_address": f"{customer.billing_address.street}, {customer.billing_address.number} - {customer.billing_address.city}/{customer.billing_address.state}",
            "amount_brl": amount,
            "data_source": "LOCAL_PROJECTION_CACHE",
        }
        self.issued_invoices.append(invoice)
        return invoice
