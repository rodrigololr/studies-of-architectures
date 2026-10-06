"""Ponto de Entrada e Demonstração Executável - Exemplo 02: Healthcare Clinic Management.

Demonstra:
1. Módulos com Bounded Contexts estritos: Patients, Appointments, MedicalRecords, Billing.
2. Isolamento de dados altamente sensíveis (Prontuário Médico / LGPD) dentro de seu próprio módulo.
3. Comunicação reativa via In-Process Event Bus para faturamento automático de consultas concluídas.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Garante o diretório do exemplo no sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.patients import PatientsModule, RegisterPatientCommand
from modules.appointments import (
    AppointmentsModule,
    ScheduleAppointmentCommand,
    AppointmentCompletedDomainEvent,
)
from modules.medical_records import (
    MedicalRecordsModule,
    CreateMedicalRecordCommand,
)
from modules.billing import BillingModule


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 02: HEALTHCARE CLINIC MANAGEMENT")
    print("=" * 80)

    # 1. Composição do Monólito e Barramento Intra-Processo
    event_bus = InProcessEventBus()

    # Logger do barramento
    event_bus.subscribe(AppointmentCompletedDomainEvent, lambda e: print(
        f"  [EVENT BUS -> AUDIT] Consulta #{e.appointment_id} concluída. Valor: R$ {e.consultation_fee:,.2f}"
    ))

    # Inicialização dos Módulos
    patients = PatientsModule()
    appointments = AppointmentsModule(patients_module=patients, event_bus=event_bus)
    medical_records = MedicalRecordsModule()
    billing = BillingModule(patients_module=patients, event_bus=event_bus)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Cadastro de Pacientes no Módulo Patients
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Cadastro de Pacientes (Módulo Patients) ---")
    p1 = patients.register_patient(RegisterPatientCommand(
        name="Mariana Souza",
        cpf="111.222.333-44",
        insurance_plan="UNIMED",
    ))
    p2 = patients.register_patient(RegisterPatientCommand(
        name="Carlos Silva",
        cpf="555.666.777-88",
        insurance_plan="PARTICULAR",
    ))
    print(f" -> Paciente 1: {p1.name} (ID: {p1.patient_id}) | Plano: {p1.insurance_plan}")
    print(f" -> Paciente 2: {p2.name} (ID: {p2.patient_id}) | Plano: {p2.insurance_plan}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Agendamento de Consulta (Módulo Appointments)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Agendamento de Consultas Médicas ---")
    data_consulta_1 = datetime.now() + timedelta(days=1)
    appt_1 = appointments.schedule(ScheduleAppointmentCommand(
        patient_id=p1.patient_id,
        doctor_crm="CRM/SP 123456",
        appointment_time=data_consulta_1,
        consultation_fee=350.0,
    ))
    print(f"Consulta Agendada: #{appt_1.appointment_id} para {p1.name} com {appt_1.doctor_crm} (Valor: R$ {appt_1.consultation_fee:,.2f})")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Atendimento Médico e Registro Confidencial de Prontuário
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Realização do Atendimento e Prontuário Médico (LGPD) ---")
    # Dr. Roberto atende e grava diagnóstico
    rec_1 = medical_records.add_record(
        cmd=CreateMedicalRecordCommand(
            appointment_id=appt_1.appointment_id,
            patient_id=p1.patient_id,
            doctor_crm="CRM/SP 123456",
            anamnesis="Paciente relata febre de 38.5C há 3 dias e tosse produtiva.",
            icd10_diagnosis="J06.9 - Infecção Aguda das Vias Aéreas Superiores",
            prescription="Amoxicilina 500mg de 8/8h por 7 dias; Dipirona 500mg se febre.",
        ),
        requester_crm="CRM/SP 123456",
    )
    print(f"Prontuário gravado com segurança (#{rec_1.record_id}): CID {rec_1.icd10_diagnosis}")

    # Conclusão da consulta dispara evento reativo
    print("\nFinalizando consulta médica no módulo Appointments...")
    appointments.complete(appt_1.appointment_id)

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Verificação da Fatura Gerada Reativamente pelo Módulo Billing
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Faturamento Automático (Módulo Billing via EventBus) ---")
    fatura_1 = billing.get_by_appointment(appt_1.appointment_id)
    if fatura_1:
        print(f"Fatura Gerada: #{fatura_1.invoice_id}")
        print(f" -> Plano: {fatura_1.insurance_plan}")
        print(f" -> Coberto pelo Convênio (80%): R$ {fatura_1.insurance_covered_amount:,.2f}")
        print(f" -> Coparticipação do Paciente (20%): R$ {fatura_1.patient_copay_amount:,.2f}")
        print(f" -> Total Faturado: R$ {fatura_1.total_fee:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Tentativa de Violação de Sigilo Médico por Usuário Não Autorizado
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Proteção de Sigilo Médico (Tentativa de Acesso Indevido) ---")
    try:
        # Usuário administrativo sem CRM tenta ler o prontuário
        medical_records.get_patient_history(p1.patient_id, requester_crm="SECRETARIA_RECEPCAO")
    except PermissionError as e:
        print(f"Bloqueio com sucesso pelo Bounded Context: {e}")

    # --------------------------------------------------------------------------
    # CENÁRIO 6: Consulta Particular e Cobrança Integral
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 6: Consulta Particular (Cobrança Integral sem Convênio) ---")
    appt_2 = appointments.schedule(ScheduleAppointmentCommand(
        patient_id=p2.patient_id,
        doctor_crm="CRM/SP 123456",
        appointment_time=datetime.now(),
        consultation_fee=400.0,
    ))
    appointments.complete(appt_2.appointment_id)
    fatura_2 = billing.get_by_appointment(appt_2.appointment_id)
    if fatura_2:
        print(f"Fatura Particular #{fatura_2.invoice_id}:")
        print(f" -> Total: R$ {fatura_2.total_fee:,.2f} | Copay Paciente (100%): R$ {fatura_2.patient_copay_amount:,.2f}")

    print("\n" + "=" * 80)
    print(" Exemplo 02 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
