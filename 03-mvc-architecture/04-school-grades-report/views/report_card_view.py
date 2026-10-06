"""
report_card_view.py - Camada de Visão (View).

Formata o boletim escolar do aluno com diagramação de notas, médias,
frequência percentual e indicador final de aprovação.
"""

from __future__ import annotations
from typing import List, Tuple
from models.academic_model import SubjectRecord


class ReportCardView:
    @staticmethod
    def render(
        student_name: str,
        enrollment_id: str,
        records: List[SubjectRecord],
        overall_stats: Tuple[float, str],
    ) -> None:
        print("\n" + "=" * 84)
        print("🎓 COLÉGIO TÉCNICO INTEGRADO — BOLETIM ESCOLAR OFICIAL")
        print("=" * 84)
        print(f"  Aluno(a):  {student_name}")
        print(f"  Matrícula: {enrollment_id}")
        print("=" * 84)

        header = f"{'DISCIPLINA':<16} | {'1ºB':<5} | {'2ºB':<5} | {'3ºB':<5} | {'4ºB':<5} | {'MÉDIA':<6} | {'FREQ (%)':<9} | SITUAÇÃO"
        print(header)
        print("-" * 84)

        for r in records:
            g = r.grades
            avg_str = f"{r.final_average:>4.1f}"
            freq_str = f"{r.attendance_pct:>5.1f}%"
            print(
                f"{r.subject_name:<16} | {g[0]:>5.1f} | {g[1]:>5.1f} | {g[2]:>5.1f} | {g[3]:>5.1f} | {avg_str:<6} | {freq_str:<9} | {r.status.value}"
            )

        print("=" * 84)
        overall_avg, status_text = overall_stats
        print(f"  • Coeficiente Geral de Rendimento (Média Global): {overall_avg:.1f}")
        print(f"  • Resultado Final do Ano Letivo:                  {status_text}")
        print("=" * 84)
