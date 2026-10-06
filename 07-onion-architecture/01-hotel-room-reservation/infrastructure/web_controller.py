"""
infrastructure/web_controller.py - Camada 4: UI / Delivery Mechanism.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from datetime import date, datetime
from application.dto import CreateReservationCommand, CancelReservationCommand
from application.booking_service import HotelBookingApplicationService


class HotelReservationController:
    def __init__(self, booking_service: HotelBookingApplicationService) -> None:
        self.booking_service = booking_service

    def handle_post_book_room(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            check_in = date.fromisoformat(payload["check_in"])
            check_out = date.fromisoformat(payload["check_out"])

            cmd = CreateReservationCommand(
                guest_id=payload["guest_id"],
                guest_name=payload["guest_name"],
                guest_email=payload["guest_email"],
                guest_document=payload["guest_document"],
                room_number=payload["room_number"],
                check_in_date=check_in,
                check_out_date=check_out,
            )

            res = self.booking_service.book_room(cmd)

            if res.success:
                return 201, {
                    "status": "CONFIRMED",
                    "reservation_id": res.reservation_id,
                    "guest": res.guest_name,
                    "room": res.room_number,
                    "nights": res.nights_count,
                    "total_price": res.total_amount,
                    "message": res.message,
                }
            else:
                return 400, {
                    "status": res.status,
                    "message": res.message,
                }

        except Exception as err:
            return 500, {"status": "ERROR", "message": str(err)}

    def handle_post_cancel_reservation(self, reservation_id: str, now: datetime) -> Tuple[int, Dict[str, Any]]:
        cmd = CancelReservationCommand(reservation_id=reservation_id)
        res = self.booking_service.cancel_reservation(cmd, now)

        if res.success:
            return 200, {
                "status": res.status,
                "reservation_id": res.reservation_id,
                "cancellation_fee": res.cancellation_fee,
                "refunded_amount": res.refund_amount,
                "message": res.message,
            }
        else:
            return 400, {
                "status": res.status,
                "message": res.message,
            }
