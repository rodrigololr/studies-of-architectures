"""Domain Service: Otimização de cubagem e precificação de frete rodoviário."""

from typing import List, Dict
from domain.model.cargo_item import CargoItem
from domain.model.vehicle_capacity import VehicleSpecification, TruckType
from domain.model.freight_quote import FreightQuote
from domain.model.exceptions import (
    CargoOverweightException,
    VolumeExceededException,
    IncompatibleVehicleException,
)


class FreightOptimizationDomainService:
    """Serviço de Domínio puro (Ring 2 da Onion Architecture).
    
    Aplica as regras matemáticas de cubagem, dimensionamento de frotas e
    precificação regulatória sem acoplamento com banco de dados ou APIs web.
    """

    ROAD_CUBING_FACTOR = 300.0  # 300 kg por metro cúbico (Padrão Rodoviário Nacional)
    GRIS_INSURANCE_RATE = 0.003  # 0.3% sobre o valor da mercadoria (Ad-Valorem + GRIS)
    HAZARDOUS_SURCHARGE = 350.0  # Adicional de manuseio e kit de emergência
    FRAGILE_SURCHARGE = 120.0    # Adicional para acondicionamento e paletização especial

    def calculate_quote(
        self,
        items: List[CargoItem],
        truck: VehicleSpecification,
        distance_km: float,
        toll_cost: float,
    ) -> FreightQuote:
        """Calcula a cotação exata aplicando cubagem e taxas contratuais."""
        if not items:
            raise ValueError("Ao menos um item de carga deve ser fornecido para a cotação.")
        if distance_km <= 0:
            raise ValueError("Distância deve ser estritamente positiva.")

        # 1. Somatórios físicos
        total_physical_weight = sum(item.weight_kg for item in items)
        total_volume = sum(item.volume_m3 for item in items)
        total_declared_val = sum(item.declared_value for item in items)
        has_hazardous = any(item.is_hazardous for item in items)
        has_fragile = any(item.is_fragile for item in items)

        # 2. Validação da capacidade física do veículo
        if total_physical_weight > truck.max_payload_kg:
            raise CargoOverweightException(
                f"Peso total da carga ({total_physical_weight:,.1f} kg) excede a capacidade máxima "
                f"do veículo {truck.truck_type.value} ({truck.max_payload_kg:,.1f} kg)."
            )

        if total_volume > truck.max_volume_m3:
            raise VolumeExceededException(
                f"Volume total da carga ({total_volume:,.2f} m³) excede o espaço útil "
                f"do veículo {truck.truck_type.value} ({truck.max_volume_m3:,.2f} m³)."
            )

        if has_hazardous and not truck.allows_hazardous:
            raise IncompatibleVehicleException(
                f"Veículo do tipo {truck.truck_type.value} não possui certificação MOPP para carga perigosa."
            )

        # 3. Cálculo de Cubagem (Taxable Weight)
        cubed_weight = total_volume * self.ROAD_CUBING_FACTOR
        taxable_weight = max(total_physical_weight, cubed_weight)

        # 4. Cálculo dos componentes de custo
        # Custo base de deslocamento por km rodado + fator de ocupação de peso
        weight_occupation_ratio = taxable_weight / truck.max_payload_kg
        base_transport_cost = distance_km * truck.cost_per_km * (1.0 + (weight_occupation_ratio * 0.15))

        # Gerenciamento de Risco e Seguro Ad-Valorem
        gris_insurance_cost = total_declared_val * self.GRIS_INSURANCE_RATE

        # Adicionais especiais
        hazardous_fee = self.HAZARDOUS_SURCHARGE if has_hazardous else 0.0
        fragile_fee = self.FRAGILE_SURCHARGE if has_fragile else 0.0

        total_freight_cost = (
            base_transport_cost
            + toll_cost
            + gris_insurance_cost
            + hazardous_fee
            + fragile_fee
        )

        breakdown: Dict[str, float] = {
            "Frete Peso/Deslocamento": round(base_transport_cost, 2),
            "Pedágio": round(toll_cost, 2),
            "Seguro e GRIS (Ad-Valorem)": round(gris_insurance_cost, 2),
            "Taxa Carga Perigosa (MOPP)": round(hazardous_fee, 2),
            "Taxa Carga Frágil": round(fragile_fee, 2),
        }

        return FreightQuote(
            selected_truck_type=truck.truck_type,
            total_physical_weight_kg=round(total_physical_weight, 2),
            total_volume_m3=round(total_volume, 3),
            taxable_weight_kg=round(taxable_weight, 2),
            distance_km=distance_km,
            base_transport_cost=round(base_transport_cost, 2),
            toll_cost=round(toll_cost, 2),
            gris_and_insurance_cost=round(gris_insurance_cost, 2),
            hazardous_fee=round(hazardous_fee, 2),
            fragile_fee=round(fragile_fee, 2),
            total_freight_cost=round(total_freight_cost, 2),
            breakdown=breakdown,
        )
