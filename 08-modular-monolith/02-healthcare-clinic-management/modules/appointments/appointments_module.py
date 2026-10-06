"""Ponto de Entrada e Facade do Módulo Appointments."""

import uuid
from typing import Optional
from shared.events import InProcessEventBus
from modules.patients.public_contracts import IPatientsModule
from modules.appointments.public_contracts import (
    IAppointmentsModule,
    ScheduleAppointmentCommand,
    AppointmentSummaryDto,
    AppointmentCompletedDomainEvent,
)
from modules.appointments.internal.appointments_internal import (
    _InternalAppointment,
    _InternalAppointmentRepository,
)


class AppointmentsModule(IAppointmentsModule):
    def __init__(self, patients_module: IPatientsModule, event_bus: InProcessEventBus) -> None:
        self._patients = patients_module
        self._bus = event_bus
        self._repo = _InternalAppointmentRepository()

    def schedule(self, cmd: ScheduleAppointmentCommand) -> AppointmentSummaryDto:
        # Verifica se o paciente existe via contrato público do módulo Patients
        patient = self._patients.get_patient(cmd.patient_id)
        if not patient or not patient.is_active:
            raise ValueError(f"Paciente #{cmd.patient_id} não cadastrado ou inativo.")

        appt_id = f"APT_{uuid.uuid4().hex[:8].upper()}"
        appt = _InternalAppointment(
            appointment_id=appt_id,
            patient_id=cmd.patient_id,
            doctor_crm=cmd.doctor_crm,
            appointment_time=cmd.appointment_time,
            status="SCHEDULED",
            consultation_fee=cmd.consultation_fee,
        )
        self._repo.save(appt)

        return AppointmentSummaryDto(
            appointment_id=appt.appointment_id,
            patient_id=appt.patient_id,
            doctor_crm=appt.doctor_crm,
            appointment_time=appt.appointment_time,
            status=appt.status,
            consultation_fee=appt.consultation_fee,
        )

    def complete(self, appointment_id: str) -> AppointmentSummaryDto:
        appt = self._repo.find_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Agendamento #{appointment_id} não encontrado.")
        if appt.status != "SCHEDULED":
            raise ValueError(f"Agendamento com status '{appt.status}' não pode ser concluído.")

        appt.status = "COMPLETED"
        self._repo.save(appt)

        # Publica evento para notificar Billing reativamente
        self._bus.publish(AppointmentCompletedDomainEvent(
            appointment_id=appt.appointment_id,
            patient_id=appt.patient_id,
            doctor_crm=appt.doctor_crm,
            consultation_fee=appt.consultation_fee,
        ))

        return AppointmentSummaryDto(
            appointment_id=appt.appointment_id,
            patient_id=appt.patient_id,
            doctor_crm=appt.doctor_crm,
            appointment_time=appt.appointment_time,
            status=appt.status,
            consultation_fee=appt.consultation_fee,
        )

    def get_by_id(self, appointment_id: str) -> Optional[AppointmentSummaryDto]:
        appt = self._repo.find_by_id(appointment_id)
        if not appt:
            return None
        return AppointmentSummaryDto(
            appointment_id=appt.appointment_id,
            patient_id=appt.patient_id,
            doctor_crm=appt.doctor_crm,
            appointment_time=appt.appointment_time,
            status=appt.status,
            consultation_fee=appt.consultation_fee,
        )
