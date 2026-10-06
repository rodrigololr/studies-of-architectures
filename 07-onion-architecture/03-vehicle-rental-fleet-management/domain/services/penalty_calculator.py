"""
domain/services/penalty_calculator.py - Camada 2: Domain Services.

Motor de regras de vistoria, combustível faltante, quilometragem excedente e avarias.
"""

from __future__ import annotations
from typing import Tuple, Dict
from domain.model.inspection import InspectionReport


class RentalPenaltyAndFuelPolicyService:
    DAILY_KM_ALLOWANCE = 200.0   # 200 km por diária contratada
    EXTRA_KM_RATE = 0.85         # R$ 0,85 por km excedente
    FUEL_EIGHTH_RATE = 35.00     # R$ 35,00 por oitavo (1/8) de tanque
    REFUELING_SERVICE_FEE = 25.0 # Taxa administrativa de reabastecimento no pátio
    DAMAGE_ITEM_COST = 250.00    # R$ 250,00 por avaria/risco constatado em vistoria

    @classmethod
    def calculate_checkin_penalties(
        cls,
        checkout: InspectionReport,
        checkin: InspectionReport,
        rental_days: int,
    ) -> Tuple[float, Dict[str, float]]:
        breakdown: Dict[str, float] = {}
        total_extras = 0.0

        # 1. Apuração de Quilometragem
        km_driven = max(0.0, checkin.odometer_km - checkout.odometer_km)
        km_limit = rental_days * cls.DAILY_KM_ALLOWANCE
        excess_km = max(0.0, km_driven - km_limit)

        if excess_km > 0:
            km_fee = round(excess_km * cls.EXTRA_KM_RATE, 2)
            breakdown[f"Quilometragem Excedente ({excess_km:.1f} km)"] = km_fee
            total_extras += km_fee

        # 2. Apuração de Combustível
        fuel_missing = max(0, checkout.fuel_level_eighths - checkin.fuel_level_eighths)
        if fuel_missing > 0:
            fuel_cost = round((fuel_missing * cls.FUEL_EIGHTH_RATE) + cls.REFUELING_SERVICE_FEE, 2)
            breakdown[f"Combustível Faltante ({fuel_missing}/8)"] = fuel_cost
            total_extras += fuel_cost

        # 3. Apuração de Avarias
        new_damages_count = len(checkin.damages)
        if new_damages_count > 0:
            damage_cost = round(new_damages_count * cls.DAMAGE_ITEM_COST, 2)
            breakdown[f"Avarias Constatadas ({new_damages_count} itens)"] = damage_cost
            total_extras += damage_cost

        return round(total_extras, 2), breakdown
