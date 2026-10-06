"""Ponto de Entrada e Facade do Módulo Procurement."""

import uuid
from shared.events import InProcessEventBus
from modules.procurement.public_contracts import (
    IProcurementModule,
    CreatePurchaseOrderCommand,
    PurchaseOrderDto,
    PurchaseOrderReceivedDomainEvent,
)
from modules.procurement.internal.procurement_internal import (
    _InternalPO,
    _InternalProcurementRepository,
)


class ProcurementModule(IProcurementModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalProcurementRepository()

    def create_order(self, cmd: CreatePurchaseOrderCommand) -> PurchaseOrderDto:
        po_number = f"PO_{uuid.uuid4().hex[:8].upper()}"
        po = _InternalPO(
            po_number=po_number,
            supplier_name=cmd.supplier_name,
            items=cmd.items,
        )
        self._repo.save(po)
        return PurchaseOrderDto(
            po_number=po.po_number,
            supplier_name=po.supplier_name,
            items=po.items,
            total_cost=po.total_cost,
            status=po.status,
        )

    def receive_order(self, po_number: str) -> PurchaseOrderDto:
        po = self._repo.find_by_number(po_number)
        if not po:
            raise ValueError(f"Ordem de Compra #{po_number} não encontrada.")
        if po.status != "PLACED":
            raise ValueError(f"Ordem com status '{po.status}' não pode ser recebida.")

        po.status = "RECEIVED"
        self._repo.save(po)

        # Publica evento de remessa entregue para o Armazém estocar
        self._bus.publish(PurchaseOrderReceivedDomainEvent(
            po_number=po.po_number,
            supplier_name=po.supplier_name,
            items=po.items,
        ))

        return PurchaseOrderDto(
            po_number=po.po_number,
            supplier_name=po.supplier_name,
            items=po.items,
            total_cost=po.total_cost,
            status=po.status,
        )
