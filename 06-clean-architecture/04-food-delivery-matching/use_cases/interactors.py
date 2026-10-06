"""
use_cases/interactors.py - Camada 2: Interactor de Matching de Entregadores.
"""

from __future__ import annotations
from datetime import datetime, timezone
from entities.models import GeoLocation, DeliveryOrder, OrderStatus
from use_cases.dto import MatchCourierRequestModel, MatchCourierResponseModel
from use_cases.boundaries import (
    MatchCourierInputBoundary,
    MatchCourierOutputBoundary,
    RestaurantRepositoryGateway,
    CourierRepositoryGateway,
    OrderRepositoryGateway,
)


class MatchCourierInteractor(MatchCourierInputBoundary):
    def __init__(
        self,
        restaurant_repo: RestaurantRepositoryGateway,
        courier_repo: CourierRepositoryGateway,
        order_repo: OrderRepositoryGateway,
        presenter: MatchCourierOutputBoundary,
    ) -> None:
        self.restaurant_repo = restaurant_repo
        self.courier_repo = courier_repo
        self.order_repo = order_repo
        self.presenter = presenter

    def execute(self, request: MatchCourierRequestModel) -> None:
        # 1. Localiza Restaurante
        restaurant = self.restaurant_repo.find_by_id(request.restaurant_id)
        if not restaurant:
            self.presenter.present(MatchCourierResponseModel(
                success=False,
                order_id=request.order_id,
                assigned_courier_name=None,
                courier_vehicle=None,
                distance_to_restaurant_km=None,
                trip_distance_km=None,
                delivery_fee=0.0,
                courier_payout=0.0,
                message=f"Restaurante '{request.restaurant_id}' não encontrado.",
            ))
            return

        # 2. Cria Entidade DeliveryOrder
        customer_loc = GeoLocation(request.customer_latitude, request.customer_longitude)
        order = DeliveryOrder(
            order_id=request.order_id,
            restaurant=restaurant,
            customer_location=customer_loc,
            items_subtotal=request.items_subtotal,
            status=OrderStatus.PENDING_MATCH,
            created_at=datetime.now(timezone.utc),
        )

        # 3. Busca Entregadores Disponíveis (Gateway)
        available_couriers = self.courier_repo.list_available_couriers()

        # 4. Avalia Distâncias e Elegibilidade nas Entidades
        candidates = []
        for courier in available_couriers:
            dist_to_rest = courier.location.distance_km_to(restaurant.location)
            if courier.is_eligible_for_dispatch(dist_to_rest, request.max_search_radius_km):
                candidates.append((courier, dist_to_rest))

        # Se nenhum entregador encontrado no raio
        if not candidates:
            order.status = OrderStatus.UNMATCHED
            self.order_repo.save(order)
            self.presenter.present(MatchCourierResponseModel(
                success=False,
                order_id=order.order_id,
                assigned_courier_name=None,
                courier_vehicle=None,
                distance_to_restaurant_km=None,
                trip_distance_km=None,
                delivery_fee=0.0,
                courier_payout=0.0,
                message=f"Nenhum entregador disponível no raio de {request.max_search_radius_km} km.",
            ))
            return

        # 5. Seleciona o Entregador Mais Próximo
        candidates.sort(key=lambda item: item[1])
        best_courier, dist_to_restaurant = candidates[0]

        # 6. Atualiza Estado do Entregador
        best_courier.is_busy = True
        self.courier_repo.update_courier(best_courier)

        # 7. Calcula Distância da Corrida e Taxas
        trip_distance = restaurant.location.distance_km_to(customer_loc)
        fee, payout = order.calculate_fees(trip_distance)
        order.status = OrderStatus.ASSIGNED
        order.assigned_courier_id = best_courier.courier_id

        # 8. Persiste Pedido e Apresenta Resposta
        self.order_repo.save(order)

        self.presenter.present(MatchCourierResponseModel(
            success=True,
            order_id=order.order_id,
            assigned_courier_name=best_courier.name,
            courier_vehicle=best_courier.vehicle.value,
            distance_to_restaurant_km=dist_to_restaurant,
            trip_distance_km=trip_distance,
            delivery_fee=fee,
            courier_payout=payout,
            message=f"Entregador {best_courier.name} alocado com sucesso ao pedido {order.order_id}!",
        ))
