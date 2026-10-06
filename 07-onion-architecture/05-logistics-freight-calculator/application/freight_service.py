"""Application Service: Casos de uso de cotação e contratação de fretes."""

import uuid
from typing import List
from domain.model.cargo_item import CargoItem
from domain.model.vehicle_capacity import TruckType
from domain.model.freight_order import FreightOrder, FreightOrderStatus
from domain.model.exceptions import FreightDomainException
from domain.services.freight_optimizer import FreightOptimizationDomainService
from application.interfaces import (
    IFreightOrderRepository,
    IVehicleSpecificationRepository,
    ITollRateApiGateway,
)
from application.dtos import (
    CalculateFreightQuoteCommand,
    FreightQuoteResponseDto,
    ConfirmFreightOrderCommand,
    FreightOrderResponseDto,
)


class FreightApplicationService:
    """Serviço da Aplicação (Ring 3 da Onion Architecture).
    
    Orquestra as chamadas externas de pedágio, consulta a especificação da frota,
    delega o cálculo e cubagem para o Domain Service e persiste o pedido.
    """

    def __init__(
        self,
        order_repo: IFreightOrderRepository,
        vehicle_repo: IVehicleSpecificationRepository,
        toll_gateway: ITollRateApiGateway,
        optimizer_service: FreightOptimizationDomainService,
    ) -> None:
        self._order_repo = order_repo
        self._vehicle_repo = vehicle_repo
        self._toll_gateway = toll_gateway
        self._optimizer_service = optimizer_service

    def calculate_and_create_quote(self, cmd: CalculateFreightQuoteCommand) -> FreightQuoteResponseDto:
        """Processa comando de cotação, calcula via Domain Service e registra ordem pendente."""
        try:
            truck_enum = TruckType[cmd.truck_type.upper()]
        except KeyError:
            raise FreightDomainException(f"Tipo de caminhão '{cmd.truck_type}' é desconhecido.")

        vehicle_spec = self._vehicle_repo.get_by_type(truck_enum)
        if not vehicle_spec:
            raise FreightDomainException(f"Especificação técnica não encontrada para veículo {truck_enum.value}.")

        # Mapeia DTOs para modelos de domínio puros
        domain_items: List[CargoItem] = [
            CargoItem(
                description=it.description,
                weight_kg=it.weight_kg,
                length_m=it.length_m,
                width_m=it.width_m,
                height_m=it.height_m,
                declared_value=it.declared_value,
                is_hazardous=it.is_hazardous,
                is_fragile=it.is_fragile,
            )
            for it in cmd.items
        ]

        # Consulta pedágios no gateway externo
        toll_cost = self._toll_gateway.calculate_tolls(
            cmd.origin_city, cmd.destination_city, truck_enum
        )

        # Invoca o serviço de domínio puro (Ring 2)
        quote = self._optimizer_service.calculate_quote(
            items=domain_items,
            truck=vehicle_spec,
            distance_km=cmd.distance_km,
            toll_cost=toll_cost,
        )

        order_id = f"FRT_{uuid.uuid4().hex[:8].upper()}"
        order = FreightOrder(
            order_id=order_id,
            shipper_name=cmd.shipper_name,
            origin_city=cmd.origin_city,
            destination_city=cmd.destination_city,
            distance_km=cmd.distance_km,
            items=domain_items,
            quote=quote,
            status=FreightOrderStatus.QUOTED,
        )

        self._order_repo.save(order)

        return FreightQuoteResponseDto(
            quote_id=order_id,
            truck_type=quote.selected_truck_type.value,
            physical_weight_kg=quote.total_physical_weight_kg,
            volume_m3=quote.total_volume_m3,
            taxable_weight_kg=quote.taxable_weight_kg,
            distance_km=quote.distance_km,
            breakdown=quote.breakdown,
            total_freight_cost=quote.total_freight_cost,
        )

    def confirm_order(self, cmd: ConfirmFreightOrderCommand) -> FreightOrderResponseDto:
        """Confirma o pedido de frete cotado para despacho."""
        order = self._order_repo.get_by_id(cmd.order_id)
        if not order:
            raise FreightDomainException(f"Ordem de frete #{cmd.order_id} não encontrada.")

        order.confirm_dispatch()
        self._order_repo.save(order)

        return FreightOrderResponseDto(
            order_id=order.order_id,
            status=order.status.value,
            shipper_name=order.shipper_name,
            origin_city=order.origin_city,
            destination_city=order.destination_city,
            total_cost=order.quote.total_freight_cost,
            message="Ordem de frete confirmada com sucesso para embarque imediato.",
        )
