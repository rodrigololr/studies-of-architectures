"""
application/booking_service.py - Camada 3: Application Service (Orquestrador de Casos de Uso).

Na Onion Architecture, o Application Service orquestra as operações entre repositórios,
serviços de domínio e serviços externos, mantendo-se livre de lógica de negócios corporativa.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.model.guest import Guest
from domain.model.reservation import Reservation, DateRange, ReservationStatus
from domain.services.pricing_service import HotelPricingService
from domain.services.cancellation_policy import CancellationPolicyService
from application.interfaces import IRoomRepository, IReservationRepository, IPaymentService
from application.dto import (
    CreateReservationCommand,
    ReservationResponseDto,
    CancelReservationCommand,
    CancelReservationResponseDto,
)


class HotelBookingApplicationService:
    def __init__(
        self,
        room_repo: IRoomRepository,
        reservation_repo: IReservationRepository,
        payment_service: IPaymentService,
    ) -> None:
        self.room_repo = room_repo
        self.reservation_repo = reservation_repo
        self.payment_service = payment_service

    def book_room(self, command: CreateReservationCommand) -> ReservationResponseDto:
        # 1. Localiza Quarto
        room = self.room_repo.find_by_number(command.room_number)
        if not room:
            return ReservationResponseDto(
                success=False,
                reservation_id=None,
                guest_name=command.guest_name,
                room_number=command.room_number,
                nights_count=0,
                total_amount=0.0,
                status="FAILED",
                message=f"Quarto {command.room_number} não cadastrado.",
            )

        # 2. Cria Value Object de Período
        try:
            period = DateRange(command.check_in_date, command.check_out_date)
        except ValueError as err:
            return ReservationResponseDto(
                success=False,
                reservation_id=None,
                guest_name=command.guest_name,
                room_number=command.room_number,
                nights_count=0,
                total_amount=0.0,
                status="FAILED",
                message=str(err),
            )

        # 3. Verifica Conflito de Disponibilidade no Período
        existing = self.reservation_repo.find_by_room_and_period(room.room_number, period)
        active_conflicts = [r for r in existing if r.status != ReservationStatus.CANCELLED]
        if active_conflicts or not room.is_available():
            return ReservationResponseDto(
                success=False,
                reservation_id=None,
                guest_name=command.guest_name,
                room_number=room.room_number,
                nights_count=period.total_nights,
                total_amount=0.0,
                status="UNAVAILABLE",
                message=f"Quarto {room.room_number} indisponível para o período de {period.check_in} a {period.check_out}.",
            )

        # 4. Invocação do Domain Service (Cálculo Sazonal de Preço)
        total_stay_cost = HotelPricingService.calculate_total_stay_price(room, period)

        # 5. Cobrança Financeira (Interface da Casca de Infraestrutura)
        paid = self.payment_service.process_charge(
            guest_id=command.guest_id,
            amount=total_stay_cost,
            description=f"Reserva Quarto {room.room_number} ({period.total_nights} diárias)",
        )
        if not paid:
            return ReservationResponseDto(
                success=False,
                reservation_id=None,
                guest_name=command.guest_name,
                room_number=room.room_number,
                nights_count=period.total_nights,
                total_amount=total_stay_cost,
                status="PAYMENT_DECLINED",
                message="Falha no processamento do pagamento da reserva.",
            )

        # 6. Criação da Entidade Reservation
        res_id = f"RES_{uuid.uuid4().hex[:8].upper()}"
        guest = Guest(
            guest_id=command.guest_id,
            name=command.guest_name,
            email=command.guest_email,
            document_cpf_or_passport=command.guest_document,
        )
        reservation = Reservation(
            reservation_id=res_id,
            guest=guest,
            room=room,
            period=period,
            total_amount=total_stay_cost,
            status=ReservationStatus.CONFIRMED,
        )

        # 7. Persistência
        self.reservation_repo.save(reservation)

        return ReservationResponseDto(
            success=True,
            reservation_id=res_id,
            guest_name=guest.name,
            room_number=room.room_number,
            nights_count=period.total_nights,
            total_amount=total_stay_cost,
            status=reservation.status.value,
            message="Reserva confirmada com sucesso!",
        )

    def cancel_reservation(self, command: CancelReservationCommand, now: datetime) -> CancelReservationResponseDto:
        # 1. Busca Reserva
        reservation = self.reservation_repo.find_by_id(command.reservation_id)
        if not reservation:
            return CancelReservationResponseDto(
                success=False,
                reservation_id=command.reservation_id,
                status="NOT_FOUND",
                cancellation_fee=0.0,
                refund_amount=0.0,
                message=f"Reserva '{command.reservation_id}' não localizada.",
            )

        if reservation.status == ReservationStatus.CANCELLED:
            return CancelReservationResponseDto(
                success=False,
                reservation_id=reservation.reservation_id,
                status=reservation.status.value,
                cancellation_fee=reservation.cancellation_fee,
                refund_amount=reservation.refund_amount,
                message="A reserva já havia sido cancelada anteriormente.",
            )

        # 2. Invocação do Domain Service (Política de Cancelamento e Multas)
        fee, refund = CancellationPolicyService.calculate_cancellation(reservation, now)

        # 3. Processamento do Reembolso se houver valor
        if refund > 0:
            self.payment_service.process_refund(reservation.guest.guest_id, refund)

        # 4. Atualização da Entidade
        reservation.cancel(fee=fee, refund=refund)
        self.reservation_repo.save(reservation)
        self.room_repo.save(reservation.room)

        return CancelReservationResponseDto(
            success=True,
            reservation_id=reservation.reservation_id,
            status=reservation.status.value,
            cancellation_fee=fee,
            refund_amount=refund,
            message="Reserva cancelada conforme a política de reembolso.",
        )
