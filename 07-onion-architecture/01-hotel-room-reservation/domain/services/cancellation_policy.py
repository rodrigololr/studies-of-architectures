"""
domain/services/cancellation_policy.py - Camada 2: Domain Services.

Regra corporativa de cálculo de multa e reembolso conforme antecedência do cancelamento.
"""

from __future__ import annotations
from datetime import datetime, date
from domain.model.reservation import Reservation


class CancellationPolicyService:
    @staticmethod
    def calculate_cancellation(
        reservation: Reservation,
        cancellation_datetime: datetime,
    ) -> tuple[float, float]:
        """
        Retorna (taxa_multa, valor_reembolso):
        - >= 48 horas antes do check-in: Reembolso integral (100%), Multa 0.
        - Entre 24h e 48h antes do check-in: Reembolso parcial (50%), Multa 50%.
        - Menos de 24h antes ou No-Show: Retenção total (100% de multa), Reembolso 0.
        """
        check_in_dt = datetime.combine(
            reservation.period.check_in,
            datetime.min.time(),
            tzinfo=cancellation_datetime.tzinfo,
        )

        hours_before_checkin = (check_in_dt - cancellation_datetime).total_seconds() / 3600.0

        if hours_before_checkin >= 48.0:
            fee = 0.0
            refund = reservation.total_amount
        elif hours_before_checkin >= 24.0:
            fee = round(reservation.total_amount * 0.50, 2)
            refund = round(reservation.total_amount * 0.50, 2)
        else:
            fee = reservation.total_amount
            refund = 0.0

        return fee, refund
