"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import Question, Exam, Student
from interface_adapters.gateways import (
    InMemoryExamRepository,
    InMemoryStudentRepository,
    InMemoryCertificateRepository,
)
from interface_adapters.presenters import ExamGradingPresenter
from interface_adapters.controllers import ExamSubmissionController
from use_cases.interactors import GradeExamInteractor


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 05: ONLINE EXAM GRADING & CERTIFICATION")
    print("=" * 80)

    # 1. Configuração do Exame de Certificação
    cert_exam = Exam(
        exam_id="EXAM-CLEAN-ARCH-2026",
        title="Certificação Profissional em Clean Architecture e SOLID",
        min_passing_percent=70.0,
        questions=[
            Question("Q1", "Qual a regra fundamental da Clean Architecture?", weight=2.0, correct_choice="C"),
            Question("Q2", "Em qual camada se localizam os Presenters e Controllers?", weight=2.0, correct_choice="B"),
            Question("Q3", "As entidades de domínio podem importar o SQLAlchemy ou Django?", weight=3.0, correct_choice="A"),
            Question("Q4", "Qual a função do Interactor no padrão de Uncle Bob?", weight=3.0, correct_choice="D"),
        ],
    )

    exam_repo = InMemoryExamRepository({
        cert_exam.exam_id: cert_exam,
    })

    student_repo = InMemoryStudentRepository({
        "std_carlos": Student(student_id="std_carlos", name="Carlos Drummond", email="carlos@poesia.com"),
        "std_ana": Student(student_id="std_ana", name="Ana Beatriz", email="ana@estudos.edu"),
    })

    cert_repo = InMemoryCertificateRepository()
    presenter = ExamGradingPresenter()

    # 2. Montagem dos Casos de Uso e Controladores
    use_case = GradeExamInteractor(
        exam_repo=exam_repo,
        student_repo=student_repo,
        certificate_repo=cert_repo,
        presenter=presenter,
    )
    controller = ExamSubmissionController(grade_exam_use_case=use_case)

    print("\n--- CENÁRIO 1: Aluno Gabaritando a Prova (Aprovação com 100% e Certificado) ---")
    controller.handle_post_exam_submit({
        "exam_id": "EXAM-CLEAN-ARCH-2026",
        "student_id": "std_carlos",
        "answers": {
            "Q1": "C",
            "Q2": "B",
            "Q3": "A",
            "Q4": "D",
        },
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    cert_id = presenter.response_body["result"]["certificate_code"]

    print("\n--- CENÁRIO 2: Aluna com Rendimento Abaixo do Corte (Reprovação sem Certificado) ---")
    controller.handle_post_exam_submit({
        "exam_id": "EXAM-CLEAN-ARCH-2026",
        "student_id": "std_ana",
        "answers": {
            "Q1": "C",  # Certa (2.0)
            "Q2": "B",  # Certa (2.0)
            "Q3": "D",  # Errada
            "Q4": "A",  # Errada
        },
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Exame Inexistente no Catálogo ---")
    controller.handle_post_exam_submit({
        "exam_id": "EXAM-FANTASMA",
        "student_id": "std_carlos",
        "answers": {},
    })
    print(f"HTTP Status: {presenter.status_code} | Resposta: {presenter.response_body}")

    print("\n--- CENÁRIO 4: Auditoria do Certificado Emitido no Repositório ---")
    saved_cert = cert_repo.find_by_id(cert_id)
    if saved_cert:
        print(f"Certificado localizado no Repositório Oficial:")
        print(f" -> Código: {saved_cert.certificate_id}")
        print(f" -> Titular: {saved_cert.student_name}")
        print(f" -> Exame: {saved_cert.exam_title}")
        print(f" -> Nota: {saved_cert.score_percent:.1f}%")
        print(f" -> Emitido em: {saved_cert.issued_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    print("\n" + "=" * 80)
    print(" Exemplo 05 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
