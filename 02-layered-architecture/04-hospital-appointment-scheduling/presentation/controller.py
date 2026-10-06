"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de agendamento e cancelamento de consultas,
mapeando conflitos de agenda para HTTP 409 Conflict.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import SchedulingService
from business.exceptions import (
    BusinessException,
    ScheduleConflictException,
    PastDateException,
    AppointmentNotFoundException,
)


class SchedulingController:
    def __init__(self, service: SchedulingService) -> None:
        self.service = service

    def schedule_appointment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/appointments"""
        try:
            app = self.service.schedule(
                patient_id=payload.get("patient_id", ""),
                doctor_id=payload.get("doctor_id", ""),
                doctor_specialty=payload.get("doctor_specialty", "Clínica Geral"),
                slot_iso=payload.get("slot_iso", ""),
                reason=payload.get("reason", "Consulta de rotina"),
            )
            return {
                "status_code": 201,
                "data": {
                    "appointment_id": app.appointment_id,
                    "patient_id": app.patient_id,
                    "doctor_id": app.doctor_id,
                    "slot_iso": app.slot_iso,
                    "status": app.status.value,
                },
            }
        except ScheduleConflictException as ex:
            return {"status_code": 409, "error": str(ex)}  # 409 Conflict
        except PastDateException as ex:
            return {"status_code": 400, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """PATCH /api/appointments/{id}/cancel"""
        try:
            app = self.service.cancel(appointment_id)
            return {
                "status_code": 200,
                "data": {"appointment_id": app.appointment_id, "status": app.status.value},
            }
        except AppointmentNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}
