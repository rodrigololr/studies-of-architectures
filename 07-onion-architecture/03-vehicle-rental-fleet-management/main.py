"""
main.py - Camada 4: Infrastructure (Composition Root da Onion Architecture).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from domain.model.vehicle import Vehicle, VehicleCategory
from infrastructure.repositories import InMemoryVehicleRepository, InMemoryRentalContractRepository
from infrastructure.payment_gateway import MockPaymentSettlementGateway
from infrastructure.rental_controller import RentalFleetController
from application.rental_service import RentalFleetApplicationService


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 03: VEHICLE RENTAL FLEET & INSPECTION")
    print("=" * 80)

    # 1. Veículos no Pátio (Infraestrutura)
    vehicle_repo = InMemoryVehicleRepository({
        "veh_jeep": Vehicle(
            vehicle_id="veh_jeep",
            license_plate="BRA-2E19",
            model_name="Jeep Renegade Longitude 1.3 Turbo",
            category=VehicleCategory.SUV,
            daily_rate=220.00,
            current_odometer_km=15000.0,
            current_fuel_eighths=8,
        ),
        "veh_onix": Vehicle(
            vehicle_id="veh_onix",
            license_plate="SP-9A88",
            model_name="Chevrolet Onix LTZ 1.0 Turbo",
            category=VehicleCategory.COMPACT,
            daily_rate=130.00,
            current_odometer_km=8500.0,
            current_fuel_eighths=8,
        ),
    })

    contract_repo = InMemoryRentalContractRepository()
    payment_gw = MockPaymentSettlementGateway()

    # 2. Application Service
    rental_service = RentalFleetApplicationService(
        vehicle_repo=vehicle_repo,
        contract_repo=contract_repo,
        payment_gateway=payment_gw,
    )

    controller = RentalFleetController(rental_service=rental_service)

    print("\n--- CENÁRIO 1: Abertura de Locação (Jeep Renegade por 2 dias) ---")
    status, open_res = controller.handle_post_open_rental({
        "customer": "Eduardo Paes",
        "vehicle_id": "veh_jeep",
        "days": 2,
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(open_res, indent=2, ensure_ascii=False))
    contract_id_1 = open_res["contract_id"]

    print("\n--- CENÁRIO 2: Devolução Perfeita (Hodômetro dentro da franquia e tanque cheio) ---")
    # Franquia de 2 dias = 400 km. Devolvido com 15.300 km (rodou 300 km)
    status, close_res = controller.handle_post_close_rental({
        "contract_id": contract_id_1,
        "return_odometer": 15300.0,
        "return_fuel_eighths": 8,
        "damages": [],
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(close_res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Nova Locação com Penalidades (KM Excedente, Combustível Faltante e Avaria) ---")
    _, open_onix = controller.handle_post_open_rental({
        "customer": "Fernanda Lima",
        "vehicle_id": "veh_onix",
        "days": 1,  # Franquia: 200 km
    })
    contract_id_2 = open_onix["contract_id"]

    # Devolve com 8.780 km (+280 km rodados, 80 km extras), tanque 5/8 (faltam 3/8) e 1 arranhão no pára-choque
    status, close_res_2 = controller.handle_post_close_rental({
        "contract_id": contract_id_2,
        "return_odometer": 8780.0,
        "return_fuel_eighths": 5,
        "damages": ["Arranhão profundo no pára-choque dianteiro direito"],
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(close_res_2, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Tentativa de Alugar Veículo que já está Locado ---")
    # Aluga o Jeep novamente
    _, active_jeep = controller.handle_post_open_rental({
        "customer": "Cliente A",
        "vehicle_id": "veh_jeep",
        "days": 3,
    })
    # Tentativa simultânea do Cliente B
    status, err_res = controller.handle_post_open_rental({
        "customer": "Cliente B",
        "vehicle_id": "veh_jeep",
        "days": 1,
    })
    print(f"Status HTTP: {status} | Resposta: {err_res}")

    print("\n--- CENÁRIO 5: Estado do Veículo Onix Atualizado Após Vistoria de Devolução ---")
    onix = vehicle_repo.find_by_id("veh_onix")
    if onix:
        print(f"Veículo #{onix.license_plate} ({onix.model_name}):")
        print(f" -> Status: {onix.status.value}")
        print(f" -> Hodômetro Atual: {onix.current_odometer_km:.1f} km")
        print(f" -> Combustível no Pátio: {onix.current_fuel_eighths}/8")

    print("\n" + "=" * 80)
    print(" Exemplo 03 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
