"""Ponto de Entrada e Demonstração Executável - Exemplo 06: Matrícula e Validação de Pré-Requisitos.

Demonstra os 4 anéis da Onion Architecture:
- Ring 1: Modelos de Domínio (Student, Course, Enrollment, EnrollmentDecision)
- Ring 2: Serviço de Domínio (EnrollmentEligibilityDomainService - pré-requisitos, créditos, vagas)
- Ring 3: Aplicação / Casos de Uso (AcademicEnrollmentApplicationService, Interfaces, DTOs)
- Ring 4: Infraestrutura (Repositórios em memória, Gateway de Notificação, Controller)
"""

import sys
import json
from pathlib import Path

# Garante o diretório do exemplo no sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Ring 1 - Domain Model
from domain.model.course import Course
from domain.model.student import Student

# Ring 2 - Domain Services
from domain.services.enrollment_validator import EnrollmentEligibilityDomainService

# Ring 3 - Application
from application.enrollment_service import AcademicEnrollmentApplicationService
from application.dtos import (
    EnrollStudentCommand,
    DropEnrollmentCommand,
)

# Ring 4 - Infrastructure
from infrastructure.in_memory_repositories import (
    InMemoryStudentRepository,
    InMemoryCourseRepository,
    InMemoryEnrollmentRepository,
)
from infrastructure.notification_gateway import MockAcademicNotificationGateway
from infrastructure.controller import AcademicEnrollmentController


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 06: EDUCATIONAL COURSE ENROLLMENT")
    print("=" * 80)

    # 1. Composição de Dependências
    student_repo = InMemoryStudentRepository()
    course_repo = InMemoryCourseRepository()
    enrollment_repo = InMemoryEnrollmentRepository()
    notification_gateway = MockAcademicNotificationGateway()

    # Ring 2 no centro
    eligibility_service = EnrollmentEligibilityDomainService()

    # Ring 3 orquestrando
    app_service = AcademicEnrollmentApplicationService(
        student_repo=student_repo,
        course_repo=course_repo,
        enrollment_repo=enrollment_repo,
        notification_gateway=notification_gateway,
        eligibility_service=eligibility_service,
    )

    # Ring 4 na borda externa
    controller = AcademicEnrollmentController(enrollment_service=app_service)

    # 2. Carga inicial do Catálogo de Cursos
    mat101 = Course(
        course_id="CRS_MAT101",
        code="MAT101",
        title="Cálculo Diferencial e Integral I",
        credits=4,
        capacity=30,
        prerequisite_ids=set(),
    )
    mat102 = Course(
        course_id="CRS_MAT102",
        code="MAT102",
        title="Cálculo Diferencial e Integral II",
        credits=4,
        capacity=30,
        prerequisite_ids={"CRS_MAT101"},  # Requer Cálculo I
    )
    ia301 = Course(
        course_id="CRS_IA301",
        code="IA301",
        title="Inteligência Artificial e Redes Neurais",
        credits=6,
        capacity=1,  # Apenas 1 vaga para testar fila de espera
        prerequisite_ids=set(),
    )

    course_repo.save(mat101)
    course_repo.save(mat102)
    course_repo.save(ia301)

    # 3. Carga inicial de Estudantes
    # Alice: caloura, nenhum curso concluído, 0 créditos
    alice = Student(
        student_id="STU_ALICE",
        name="Alice Walker",
        registration_number="2026-ENG-001",
        max_semester_credits=24,
        current_enrolled_credits=0,
        completed_course_ids=set(),
    )
    # Bob: veterano, já concluiu MAT101
    bob = Student(
        student_id="STU_BOB",
        name="Bob Martin",
        registration_number="2025-CC-042",
        max_semester_credits=24,
        current_enrolled_credits=8,
        completed_course_ids={"CRS_MAT101"},
    )
    # Carol: estudante quase no limite de carga horária (20 créditos de 24)
    carol = Student(
        student_id="STU_CAROL",
        name="Carol Danvers",
        registration_number="2024-FIS-099",
        max_semester_credits=24,
        current_enrolled_credits=20,
        completed_course_ids={"CRS_MAT101"},
    )

    student_repo.save(alice)
    student_repo.save(bob)
    student_repo.save(carol)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Matrícula Regular sem Pré-requisito (Alice em Cálculo I)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Matrícula Regular Válida (Alice em Cálculo I) ---")
    res_1 = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_ALICE",
        course_id="CRS_MAT101",
        semester="2026.1",
    ))
    print(f"Status HTTP: {res_1['http_status']}")
    print(json.dumps(res_1["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Tentativa de Matrícula sem Cumprir Pré-Requisito Obrigatório
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Rejeição por Falta de Pré-Requisito (Alice em Cálculo II) ---")
    res_2 = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_ALICE",
        course_id="CRS_MAT102",  # Requer Cálculo I
        semester="2026.1",
    ))
    print(f"Status HTTP: {res_2['http_status']} | Resposta: {res_2['data']}")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Matrícula com Pré-Requisito Satisfeito (Bob em Cálculo II)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Matrícula Aprovada com Pré-Requisito Concluído (Bob em Cálculo II) ---")
    res_3 = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_BOB",
        course_id="CRS_MAT102",
        semester="2026.1",
    ))
    print(f"Status HTTP: {res_3['http_status']}")
    print(json.dumps(res_3["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Tentativa de Ultrapassar Teto Semestral de Créditos (Carol)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Bloqueio por Excesso de Carga Horária Semestral (Carol) ---")
    # Carol tem 20 créditos e IA301 exige 6 créditos (20 + 6 = 26 > 24)
    res_4 = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_CAROL",
        course_id="CRS_IA301",
        semester="2026.1",
    ))
    print(f"Status HTTP: {res_4['http_status']} | Resposta: {res_4['data']}")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Turma Lotada e Alocação Automática em Lista de Espera (Waitlist)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Turma com Vagas Esgotadas -> Alocação em Lista de Espera ---")
    # Bob preenche a única vaga de IA301 (capacidade = 1)
    res_bob_ia = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_BOB",
        course_id="CRS_IA301",
        semester="2026.1",
    ))
    print(f"1ª Inscrição (Bob - Ocupa Vaga): Status={res_bob_ia['data']['status']}")

    # Agora Alice tenta se inscrever na mesma turma lotada
    res_alice_ia = controller.post_enroll(EnrollStudentCommand(
        student_id="STU_ALICE",
        course_id="CRS_IA301",
        semester="2026.1",
    ))
    print(f"2ª Inscrição (Alice - Turma Cheia): HTTP {res_alice_ia['http_status']}")
    print(json.dumps(res_alice_ia["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 6: Trancamento de Disciplina e Restituição de Créditos
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 6: Trancamento de Matrícula (Alice tranca Cálculo I) ---")
    enrollment_alice_mat101 = res_1["data"]["enrollment_id"]
    res_drop = controller.post_drop(DropEnrollmentCommand(enrollment_id=enrollment_alice_mat101))
    print(f"Status HTTP: {res_drop['http_status']}")
    print(json.dumps(res_drop["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 7: Auditoria de Notificações Acadêmicas Emitidas
    # --------------------------------------------------------------------------
    print("\n--- Notificações Enviadas pelo Gateway de Infraestrutura ---")
    for notif in notification_gateway.notifications:
        print(f" -> {notif}")

    print("\n" + "=" * 80)
    print(" Exemplo 06 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
