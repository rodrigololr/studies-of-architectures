"""Ponto de Entrada e Facade do Módulo Transportation."""

import uuid
from shared.events import InProcessEventBus
from modules.warehousing.public_contracts import IWarehousingModule
from modules.transportation.public_contracts import (
    ITransportationModule,
    DispatchShipmentCommand,
    ShipmentDto,
    ShipmentDispatchedDomainEvent,
)
from modules.transportation.internal.transportation_internal import (
    _InternalShipment,
    _InternalTransportationRepository,
)


class TransportationModule(ITransportationModule):
    def __init__(
        self,
        warehousing_module: IWarehousingModule,
        event_bus: InProcessEventBus,
    ) -> None:
        self._warehousing = warehousing_module
        self._bus = event_bus
        self._repo = _InternalTransportationRepository()

    def dispatch(self, cmd: DispatchShipmentCommand) -> ShipmentDto:
        # 1. Comanda a separação física e baixa no módulo de Armazém
        has_items = self._warehousing.pick_and_pack(cmd.item_code, cmd.quantity)
        if not has_items:
            raise ValueError(
                f"Saldo insuficiente no armazém para expedir item '{cmd.item_code}'. Quantidade solicitada: {cmd.quantity}."
            )

        shipment_id = f"SHP_{uuid.uuid4().hex[:8].upper()}"
        shipment = _InternalShipment(
            shipment_id=shipment_id,
            client_name=cmd.client_name,
            destination_city=cmd.destination_city,
            truck_plate=cmd.truck_plate,
            item_code=cmd.item_code,
            quantity=cmd.quantity,
            cargo_value=cmd.cargo_value,
        )
        self._repo.save(shipment)

        # 2. Emite evento de expedição no barramento para o módulo fiscal (Invoicing)
        self._bus.publish(ShipmentDispatchedDomainEvent(
            shipment_id=shipment.shipment_id,
            client_name=shipment.client_name,
            destination_city=shipment.destination_city,
            item_code=shipment.item_code,
            quantity=shipment.quantity,
            cargo_value=shipment.cargo_value,
        ))

        return ShipmentDto(
            shipment_id=shipment.shipment_id,
            client_name=shipment.client_name,
            destination_city=shipment.destination_city,
            truck_plate=shipment.truck_plate,
            status=shipment.status,
            cargo_value=shipment.cargo_value,
        )
