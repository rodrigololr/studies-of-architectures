"""
main.py - Demonstração executável do Boletim Escolar (Padrão MVC).

Cadastra um estudante, lança as notas e frequências de 4 disciplinas
e emite o boletim oficial diagramado demonstrando aprovação, recuperação e reprovação por faltas.
"""

from models.academic_model import StudentAcademicModel
from controllers.report_card_controller import StudentReportController


def main() -> None:
    print("=" * 84)
    print("DEMONSTRAÇÃO: Arquitetura MVC (Boletim e Notas Escolares)")
    print("=" * 84)

    # 1. Instanciação dos componentes MVC para o aluno Lucas
    model = StudentAcademicModel(student_name="Lucas Souza", enrollment_id="MATR-2026-089")
    controller = StudentReportController(model)

    # 2. Lançamento de notas das disciplinas
    # Matemática: Aprovado com louvor (Média 8.5, Frequência 92%)
    controller.record_subject_performance("Matemática", 8.0, 9.0, 8.5, 8.5, attendance=92.0)

    # História: Aprovado (Média 7.3, Frequência 88%)
    controller.record_subject_performance("História", 7.0, 7.5, 6.5, 8.0, attendance=88.0)

    # Física: Em Recuperação (Média 6.0, Frequência 80%)
    controller.record_subject_performance("Física", 5.5, 6.0, 6.5, 6.0, attendance=80.0)

    # Química: Reprovado por Frequência Insuficiente (Média 7.8, Frequência 68% < 75%)
    controller.record_subject_performance("Química", 7.5, 8.0, 8.0, 7.5, attendance=68.0)

    # 3. Emissão do Boletim Escolar Oficial
    controller.print_student_report_card()


if __name__ == "__main__":
    main()
