"""Ponto de Entrada e Facade do Módulo Invoicing."""

import uuid
from typing import Optional, List
from shared.events import InProcessEventBus
from modules.transportation.public_contracts import ShipmentDispatchedDomainEvent
from modules.invoicing.public_contracts import IInvoicingModule, FiscalInvoiceDto
from modules.invoicing.internal.invoicing_internal import (
    _InternalNFe,
    _InternalInvoicingRepository,
)


class InvoicingModule(IInvoicingModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalInvoicingRepository()

        # Reage ao despacho de transporte para emitir automaticamente a NF-e
        self._bus.subscribe(ShipmentDispatchedDomainEvent, self._handle_shipment_dispatched)

    def _handle_shipment_dispatched(self, e: ShipmentDispatchedDomainEvent) -> None:
        # Cálculo tributário de ICMS (18%) e IPI (5%)
        icms = round(e.cargo_value * 0.18, 2)
        ipi = round(e.cargo_value * 0.05, 2)
        total = round(e.cargo_value + ipi, 2)  # IPI agrega ao total da nota

        nfe_key = f"NFE-3526-{uuid.uuid4().hex[:16].upper()}"
        nfe = _InternalNFe(
            nfe_key=nfe_key,
            shipment_id=e.shipment_id,
            client_name=e.client_name,
            cargo_value=e.cargo_value,
            icms_tax=icms,
            ipi_tax=ipi,
            total_amount=total,
        )
        self._repo.save(nfe)

    def get_by_shipment(self, shipment_id: str) -> Optional[FiscalInvoiceDto]:
        nfe = self._repo.find_by_shipment(shipment_id)
        if not nfe:
            return None
        return FiscalInvoiceDto(
            nfe_key=nfe.nfe_key,
            shipment_id=nfe.shipment_id,
            client_name=nfe.client_name,
            total_cargo_value=nfe.cargo_value,
            icms_tax=nfe.icms_tax,
            ipi_tax=nfe.ipi_tax,
            total_invoice_amount=nfe.total_amount,
            status=nfe.status,
        )

    def list_all(self) -> List[FiscalInvoiceDto]:
        return [
            FiscalInvoiceDto(
                nfe_key=n.nfe_key,
                shipment_id=n.shipment_id,
                client_name=n.client_name,
                total_cargo_value=n.cargo_value,
                icms_tax=n.icms_tax,
                ipi_tax=n.ipi_tax,
                total_invoice_amount=n.total_amount,
                status=n.status,
            )
            for n in self._repo.list_all()
        ]
