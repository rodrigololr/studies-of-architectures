"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import GeoLocation, Courier, Restaurant, VehicleType
from interface_adapters.gateways import (
    InMemoryRestaurantRepository,
    InMemoryCourierRepository,
    InMemoryOrderRepository,
)
from interface_adapters.presenters import DispatchRestPresenter
from interface_adapters.controllers import DeliveryDispatchController
from use_cases.interactors import MatchCourierInteractor


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 04: FOOD DELIVERY DISPATCH & MATCHING")
    print("=" * 80)

    # 1. Base Geográfica: Restaurante na Av. Paulista, São Paulo
    paulista_rest = Restaurant(
        restaurant_id="rest_paulista_pizza",
        name="Pizzaria Bella Paulista",
        location=GeoLocation(latitude=-23.561684, longitude=-46.655981),
    )
    rest_repo = InMemoryRestaurantRepository({
        paulista_rest.restaurant_id: paulista_rest,
    })

    # 2. Entregadores nas imediações
    courier_repo = InMemoryCourierRepository({
        "courier_carlos": Courier(
            courier_id="courier_carlos",
            name="Carlos Motoboy",
            location=GeoLocation(latitude=-23.565000, longitude=-46.652000),  # ~0.5 km
            vehicle=VehicleType.MOTORCYCLE,
            is_online=True,
            is_busy=False,
        ),
        "courier_lucas": Courier(
            courier_id="courier_lucas",
            name="Lucas Ciclista",
            location=GeoLocation(latitude=-23.559000, longitude=-46.660000),  # ~0.6 km
            vehicle=VehicleType.BICYCLE,
            is_online=True,
            is_busy=False,
        ),
        "courier_marcos": Courier(
            courier_id="courier_marcos",
            name="Marcos Ocupado",
            location=GeoLocation(latitude=-23.562000, longitude=-46.656000),  # ~0.1 km mas já em entrega
            vehicle=VehicleType.MOTORCYCLE,
            is_online=True,
            is_busy=True,
        ),
        "courier_rafael": Courier(
            courier_id="courier_rafael",
            name="Rafael Longe",
            location=GeoLocation(latitude=-23.610000, longitude=-46.690000),  # ~6.5 km
            vehicle=VehicleType.MOTORCYCLE,
            is_online=True,
            is_busy=False,
        ),
    })

    order_repo = InMemoryOrderRepository()
    presenter = DispatchRestPresenter()

    # 3. Montagem do Caso de Uso
    interactor = MatchCourierInteractor(
        restaurant_repo=rest_repo,
        courier_repo=courier_repo,
        order_repo=order_repo,
        presenter=presenter,
    )
    controller = DeliveryDispatchController(match_use_case=interactor)

    print("\n--- CENÁRIO 1: Matching de Pedido #01 (Cliente a ~2 km) ---")
    controller.handle_post_dispatch({
        "order_id": "ORD-DELIVERY-101",
        "restaurant_id": "rest_paulista_pizza",
        "customer_lat": -23.570000,
        "customer_lon": -46.640000,
        "subtotal": 89.90,
        "max_radius_km": 3.0,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Matching de Pedido #02 Imediato (Carlos ocupado -> Lucas Bike assume) ---")
    controller.handle_post_dispatch({
        "order_id": "ORD-DELIVERY-102",
        "restaurant_id": "rest_paulista_pizza",
        "customer_lat": -23.560000,
        "customer_lon": -46.650000,
        "subtotal": 45.00,
        "max_radius_km": 3.0,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Matching de Pedido #03 sem Entregadores no Raio (Carlos e Lucas ocupados, Rafael fora de alcance) ---")
    controller.handle_post_dispatch({
        "order_id": "ORD-DELIVERY-103",
        "restaurant_id": "rest_paulista_pizza",
        "customer_lat": -23.565000,
        "customer_lon": -46.655000,
        "subtotal": 120.00,
        "max_radius_km": 2.0,  # Rafael está a mais de 6km
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Restaurante Inexistente ---")
    controller.handle_post_dispatch({
        "order_id": "ORD-DELIVERY-999",
        "restaurant_id": "rest_fantasma",
        "customer_lat": -23.560000,
        "customer_lon": -46.650000,
    })
    print(f"HTTP Status: {presenter.status_code} | Resposta: {presenter.response_body}")

    print("\n" + "=" * 80)
    print(" Exemplo 04 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
