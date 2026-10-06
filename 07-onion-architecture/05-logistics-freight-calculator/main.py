"""Ponto de Entrada e Demonstração Executável - Exemplo 05: Cálculo de Frete e Otimização Logística.

Demonstra os 4 anéis da Onion Architecture:
- Ring 1: Modelos de Domínio (CargoItem, VehicleSpecification, FreightOrder, FreightQuote)
- Ring 2: Serviço de Domínio (FreightOptimizationDomainService - cubagem, taxas, limites)
- Ring 3: Aplicação / Casos de Uso (FreightApplicationService, Interfaces, DTOs)
- Ring 4: Infraestrutura (Repositórios em memória, Gateway de Pedágio, Controller)
"""

import sys
import json
from pathlib import Path

# Garante o diretório do exemplo no sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Ring 2 - Domain Services
from domain.services.freight_optimizer import FreightOptimizationDomainService

# Ring 3 - Application
from application.freight_service import FreightApplicationService
from application.dtos import (
    CalculateFreightQuoteCommand,
    CargoItemInputDto,
    ConfirmFreightOrderCommand,
)

# Ring 4 - Infrastructure
from infrastructure.in_memory_repositories import (
    InMemoryFreightOrderRepository,
    InMemoryVehicleSpecificationRepository,
)
from infrastructure.toll_gateway import MockNationalTollApiGateway
from infrastructure.controller import FreightCalculatorController


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 05: LOGISTICS FREIGHT & CUBING OPTIMIZER")
    print("=" * 80)

    # 1. Composição de Dependências
    order_repo = InMemoryFreightOrderRepository()
    vehicle_repo = InMemoryVehicleSpecificationRepository()
    toll_gateway = MockNationalTollApiGateway()

    # Ring 2 no centro
    optimizer_service = FreightOptimizationDomainService()

    # Ring 3 orquestrando
    app_service = FreightApplicationService(
        order_repo=order_repo,
        vehicle_repo=vehicle_repo,
        toll_gateway=toll_gateway,
        optimizer_service=optimizer_service,
    )

    # Ring 4 na casca externa
    controller = FreightCalculatorController(freight_service=app_service)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Carga Pesada de Alta Densidade (Peças de Aço - Peso Prevalece)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Carga Pesada de Aço (São Paulo -> Curitiba: 400 km) ---")
    cmd_1 = CalculateFreightQuoteCommand(
        shipper_name="Metalúrgica Gerdau",
        origin_city="Sao Paulo",
        destination_city="Curitiba",
        distance_km=400.0,
        truck_type="TRUCK",
        items=[
            CargoItemInputDto(
                description="Bobinas de Aço Laminado",
                weight_kg=8_500.0,
                length_m=2.0,
                width_m=1.5,
                height_m=1.2,
                declared_value=120_000.0,
            )
        ],
    )
    quote_1 = controller.post_quote(cmd_1)
    print(f"Status HTTP: {quote_1['http_status']}")
    print(json.dumps(quote_1["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Carga Volumosa de Baixa Densidade (Colchões - Peso Cubado Prevalece)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Carga Volumosa (Colchões e Espumas: Cubagem Prevalece) ---")
    cmd_2 = CalculateFreightQuoteCommand(
        shipper_name="Ortobom Colchões",
        origin_city="Sao Paulo",
        destination_city="Rio de Janeiro",
        distance_km=430.0,
        truck_type="TOCO",
        items=[
            CargoItemInputDto(
                description="Lote de 40 Colchões Queen Size",
                weight_kg=950.0,     # Peso físico leve: 950 kg
                length_m=4.0,
                width_m=2.2,
                height_m=2.4,       # Volume: 21.12 m3 -> Peso cubado: ~6.336 kg
                declared_value=45_000.0,
            )
        ],
    )
    quote_2 = controller.post_quote(cmd_2)
    print(f"Status HTTP: {quote_2['http_status']}")
    print(json.dumps(quote_2["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Excesso de Carga em Relação ao Limite do Veículo (Rejeição de Domínio)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Tentativa de Sobrecarga de Peso em Caminhão Truck ---")
    cmd_overweight = CalculateFreightQuoteCommand(
        shipper_name="Cimento Votoran",
        origin_city="Sao Paulo",
        destination_city="Curitiba",
        distance_km=400.0,
        truck_type="TRUCK",  # Limite máximo é 14.000 kg
        items=[
            CargoItemInputDto(
                description="Sacos de Cimento CP-II",
                weight_kg=16_500.0,  # Ultrapassa em 2.500 kg
                length_m=5.0,
                width_m=2.0,
                height_m=1.0,
                declared_value=35_000.0,
            )
        ],
    )
    res_overweight = controller.post_quote(cmd_overweight)
    print(f"Status HTTP: {res_overweight['http_status']} | Resposta: {res_overweight['data']}")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Carga Perigosa em Veículo sem Certificação MOPP (Rejeição)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Carga Química Perigosa em Veículo Urbano (VUC) Sem Certificação ---")
    cmd_haz_vuc = CalculateFreightQuoteCommand(
        shipper_name="Química Brasil",
        origin_city="Sao Paulo",
        destination_city="Sao Paulo",
        distance_km=45.0,
        truck_type="VUC",  # VUC não aceita perigosa
        items=[
            CargoItemInputDto(
                description="Tambores de Solvente Inflamável",
                weight_kg=1_200.0,
                length_m=1.5,
                width_m=1.5,
                height_m=1.0,
                declared_value=18_000.0,
                is_hazardous=True,
            )
        ],
    )
    res_haz_vuc = controller.post_quote(cmd_haz_vuc)
    print(f"Status HTTP: {res_haz_vuc['http_status']} | Resposta: {res_haz_vuc['data']}")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Cotação Interestadual Longa com Carga Perigosa e Frágil em Carreta
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Cotação Longa Especial e Despacho Confirmado ---")
    cmd_long = CalculateFreightQuoteCommand(
        shipper_name="Petroquímica do Nordeste",
        origin_city="Sao Paulo",
        destination_city="Salvador",
        distance_km=1950.0,
        truck_type="CARRETA",
        items=[
            CargoItemInputDto(
                description="Reagentes de Laboratório Frágeis e Inflamáveis",
                weight_kg=12_000.0,
                length_m=10.0,
                width_m=2.4,
                height_m=2.2,
                declared_value=380_000.0,
                is_hazardous=True,
                is_fragile=True,
            )
        ],
    )
    quote_long = controller.post_quote(cmd_long)
    print(f"Status HTTP: {quote_long['http_status']}")
    print(json.dumps(quote_long["data"], indent=2, ensure_ascii=False))

    # Confirmar e despachar a ordem gerada
    order_id = quote_long["data"]["quote_id"]
    confirm_res = controller.post_confirm_order(ConfirmFreightOrderCommand(order_id=order_id))
    print(f"\nConfirmação da Ordem #{order_id}:")
    print(f"Status HTTP: {confirm_res['http_status']}")
    print(json.dumps(confirm_res["data"], indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print(" Exemplo 05 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
