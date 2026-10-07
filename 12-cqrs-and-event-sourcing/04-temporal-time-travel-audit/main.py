import sys
from pathlib import Path
from datetime import datetime

# Inclusão do diretório para imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from domain.aggregate import EmployeeAggregate
from infrastructure.event_store import AppendOnlyEventStore
from services.time_travel_engine import TimeTravelAuditService

def main():
    print("=" * 80)
    print("EXEMPLO 04: CQRS & EVENT SOURCING - TEMPORAL TIME-TRAVEL AUDIT ENGINE")
    print("=" * 80)

    event_store = AppendOnlyEventStore()
    audit_service = TimeTravelAuditService(event_store)

    emp_id = "EMP-BR-8821"
    emp = EmployeeAggregate(emp_id)

    print(f"\n[PASSO 1] Gravando marcos históricos da carreira do colaborador '{emp_id}'...")

    # Linha do tempo de carreira ao longo de 4 anos
    emp.hire(
        timestamp=datetime(2021, 2, 1, 9, 0),
        full_name="Mariana Souza",
        role="Engenheira de Software Júnior",
        department="Mobile Apps",
        salary=5000.0,
    )
    emp.adjust_salary(
        timestamp=datetime(2021, 11, 15, 14, 30),
        new_salary=6500.0,
        justification="Avaliação de desempenho semestral positiva",
    )
    emp.promote(
        timestamp=datetime(2022, 6, 1, 10, 0),
        new_role="Engenheira de Software Pleno",
        rank_level=2,
    )
    emp.award_bonus(
        timestamp=datetime(2022, 12, 20, 16, 0),
        amount=8000.0,
        reason="Superação de metas corporativas do ano de 2022",
    )
    emp.transfer_department(
        timestamp=datetime(2023, 3, 10, 11, 0),
        new_department="Plataformas de Dados & IA",
        reason="Transição interna por projeto estratégico corporativo",
    )
    emp.adjust_salary(
        timestamp=datetime(2023, 9, 1, 15, 0),
        new_salary=11000.0,
        justification="Ajuste de equidade para o pool de Engenharia de Dados",
    )
    emp.promote(
        timestamp=datetime(2024, 5, 15, 9, 30),
        new_role="Engenheira de Software Sênior / Tech Lead",
        rank_level=3,
    )
    emp.adjust_salary(
        timestamp=datetime(2024, 5, 15, 9, 31),
        new_salary=17500.0,
        justification="Promoção para liderança técnica",
    )
    emp.award_bonus(
        timestamp=datetime(2024, 12, 20, 17, 0),
        amount=15000.0,
        reason="Bônus de liderança e entrega do novo Data Lake",
    )

    # Persiste todos os eventos no Event Store
    event_store.append_events(emp_id, emp.uncommitted_events)
    emp.clear_uncommitted_events()

    print(f" -> {len(event_store.read_stream(emp_id))} eventos históricos gravados com sucesso.")

    print("\n" + "=" * 80)
    print("[PASSO 2] LINHA DO TEMPO CRONOLÓGICA COMPLETA DE AUDITORIA (Event Stream)")
    print("=" * 80)
    for item in audit_service.get_audit_timeline(emp_id):
        print(f"  [v{item['version']:<2}] {item['timestamp']} | {item['event_type']:<22} | {item['description']}")

    print("\n" + "=" * 80)
    print("[PASSO 3] CONSULTAS PONTO-A-PONTO DE VIAGEM NO TEMPO (TIME-TRAVEL AUDITING)")
    print("=" * 80)
    print("Cenário: Auditor do Ministério do Trabalho solicita comprovação do estado funcional em 6 datas:")

    audit_dates = [
        datetime(2020, 12, 31),  # Antes da contratação
        datetime(2021, 6, 1),    # Primeiros meses como Júnior
        datetime(2022, 7, 1),    # Logo após promoção para Pleno
        datetime(2023, 4, 1),    # Logo após transferência para Plataformas de Dados
        datetime(2024, 1, 1),    # Início de 2024 (Pleno com R$ 11.000)
        datetime(2025, 1, 1),    # Presente (Tech Lead com R$ 17.500)
    ]

    print(f"\n  {'Data do Corte (As-Of)':<22} | {'Existe?':<8} | {'Cargo / Função':<35} | {'Departamento':<25} | {'Salário (R$)':>12} | {'Eventos Replay'}")
    print("  " + "-" * 125)

    for target_dt in audit_dates:
        snap = audit_service.get_employee_state_as_of(emp_id, target_dt)
        if not snap.exists:
            print(f"  {target_dt.strftime('%Y-%m-%d'):<22} | {'NÃO':<8} | {'(Colaborador ainda não admitido)':<35} | {'-':<25} | {'-':>12} | {snap.events_replayed_count}")
        else:
            print(f"  {target_dt.strftime('%Y-%m-%d'):<22} | {'SIM':<8} | {snap.role:<35} | {snap.department:<25} | {snap.salary:>12.2f} | {snap.events_replayed_count}")

    print("\n" + "=" * 80)
    print("[PASSO 4] VALIDAÇÃO DE CONFORMIDADE FISCAL ESPECÍFICA")
    print("=" * 80)
    # Suponha que o RH precise declarar à Receita Federal os bônus recebidos exatamente até 31/12/2022
    tax_cutoff = datetime(2022, 12, 31)
    tax_snap = audit_service.get_employee_state_as_of(emp_id, tax_cutoff)
    print(f"Auditoria Fiscal do Exercício 2022 (Corte em {tax_cutoff.strftime('%Y-%m-%d')}):")
    print(f"  • Cargo na Data:            {tax_snap.role}")
    print(f"  • Salário Base na Data:     R$ {tax_snap.salary:.2f}")
    print(f"  • Bônus Acumulados em 2022: R$ {tax_snap.total_bonuses:.2f}")
    assert tax_snap.total_bonuses == 8000.0, "Bônus em 2022 deveria ser exatamente R$ 8.000!"

    # E até o presente:
    present_snap = audit_service.get_employee_state_as_of(emp_id, datetime(2025, 1, 1))
    print(f"\nAuditoria Fiscal do Exercício 2024 (Corte em 2025-01-01):")
    print(f"  • Cargo na Data:            {present_snap.role}")
    print(f"  • Salário Base na Data:     R$ {present_snap.salary:.2f}")
    print(f"  • Bônus Totais Históricos:  R$ {present_snap.total_bonuses:.2f}")
    assert present_snap.total_bonuses == 23000.0, "Bônus totais deveriam ser R$ 23.000!"

    print("\n[OK] Auditoria temporal e conformidade trabalhista comprovadas com 100% de exatidão.")

if __name__ == "__main__":
    main()
