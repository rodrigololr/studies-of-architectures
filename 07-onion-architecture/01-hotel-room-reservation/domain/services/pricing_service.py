"""
domain/services/pricing_service.py - Camada 2: Domain Services.

Regra corporativa multientidade: cálculo dinâmico de diárias sazonais.
"""

from __future__ import annotations
from datetime import timedelta, date
from domain.model.room import Room
from domain.model.reservation import DateRange


class HotelPricingService:
    @staticmethod
    def calculate_total_stay_price(room: Room, period: DateRange) -> float:
        """
        Calcula o valor total da estadia aplicando tarifas diferenciadas:
        - Fins de semana (sexta e sábado): +20% sobre a diária base.
        - Meses de alta temporada (Dezembro, Janeiro, Julho): +30% sobre a diária.
        """
        current_date = period.check_in
        total_amount = 0.0

        while current_date < period.check_out:
            daily_price = room.base_daily_rate

            # Multiplicador sazonal (Alta temporada)
            if current_date.month in {1, 7, 12}:
                daily_price *= 1.30

            # Multiplicador de fim de semana (Sexta=4, Sábado=5)
            if current_date.weekday() in {4, 5}:
                daily_price *= 1.20

            total_amount += daily_price
            current_date += timedelta(days=1)

        return round(total_amount, 2)
