"""
main.py - Demonstração executável de Agendamento Hospitalar em Camadas.

Demonstra agendamento com validação de conflito de agenda (HTTP 409 Conflict),
regras de data passada e liberação de horário após cancelamento.
"""

from datetime import datetime, timedelta
from data.repository import AppointmentRepository
from business.service import SchedulingService
from presentation.controller import SchedulingController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Agendamento Hospitalar e Conflitos de Agenda")
    print("=" * 65)

    repo = AppointmentRepository()
    service = SchedulingService(repo)
    controller = SchedulingController(service)

    # Criação de horário futuro (amanhã às 14:00)
    amanha = datetime.now() + timedelta(days=1)
    horario_valido = amanha.strftime("%Y-%m-%dT14:00")

    # 1. Agendamento inicial com sucesso
    print(f"\n[PASSO 1] POST /api/appointments (Agendando para {horario_valido})...")
    req_1 = {
        "patient_id": "paciente-joao",
        "doctor_id": "dr-roberto-cardiologista",
        "doctor_specialty": "Cardiologia",
        "slot_iso": horario_valido,
        "reason": "Check-up cardiológico anual",
    }
    res_1 = controller.schedule_appointment(req_1)
    print(f"  HTTP {res_1['status_code']}: {res_1['data']}")
    app_id = res_1["data"]["appointment_id"]

    # 2. Conflito: Outro paciente tenta o mesmo médico no mesmo horário
    print(f"\n[PASSO 2] POST /api/appointments (Tentativa de agendamento em horário conflitante)...")
    req_conflito = {
        "patient_id": "paciente-maria",
        "doctor_id": "dr-roberto-cardiologista",
        "doctor_specialty": "Cardiologia",
        "slot_iso": horario_valido,
        "reason": "Avaliação de rotina",
    }
    res_conflito = controller.schedule_appointment(req_conflito)
    print(f"  HTTP {res_conflito['status_code']} Conflict: Erro = '{res_conflito['error']}'")

    # 3. Tentativa de agendamento no passado (bloqueado)
    print("\n[PASSO 3] POST /api/appointments (Tentativa de agendamento no passado)...")
    res_passado = controller.schedule_appointment({
        "patient_id": "paciente-maria",
        "doctor_id": "dr-roberto-cardiologista",
        "slot_iso": "2020-01-01T10:00",
    })
    print(f"  HTTP {res_passado['status_code']} Bad Request: Erro = '{res_passado['error']}'")

    # 4. Cancelamento da consulta inicial do João
    print(f"\n[PASSO 4] PATCH /api/appointments/{app_id}/cancel (Cancelando consulta de João)...")
    res_cancel = controller.cancel_appointment(app_id)
    print(f"  HTTP {res_cancel['status_code']}: {res_cancel['data']}")

    # 5. Maria agora consegue agendar no horário que acabou de ser liberado!
    print(f"\n[PASSO 5] POST /api/appointments (Maria reagendando no horário liberado)...")
    res_sucesso_maria = controller.schedule_appointment(req_conflito)
    print(f"  HTTP {res_sucesso_maria['status_code']}: {res_sucesso_maria['data']}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
