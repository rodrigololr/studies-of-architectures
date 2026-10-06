"""Domain Service: Validação de elegibilidade e pré-requisitos acadêmicos."""

from domain.model.course import Course
from domain.model.student import Student
from domain.model.enrollment import EnrollmentStatus, EnrollmentDecision
from domain.model.exceptions import (
    PrerequisiteNotMetException,
    CreditLimitExceededException,
    AlreadyEnrolledException,
)


class EnrollmentEligibilityDomainService:
    """Serviço de Domínio puro (Ring 2 da Onion Architecture).
    
    Centraliza a lógica de validação de grade curricular, encadeamento de
    pré-requisitos e controle de lista de espera sem acoplamento a bancos de dados.
    """

    def evaluate_eligibility(
        self,
        student: Student,
        course: Course,
        is_already_active_in_semester: bool = False,
    ) -> EnrollmentDecision:
        """Avalia se um estudante atende a todos os critérios para cursar uma disciplina."""
        # 1. Checagem de duplicação
        if student.has_completed(course.course_id):
            raise AlreadyEnrolledException(
                f"Estudante '{student.name}' já concluiu a disciplina '{course.title}' anteriormente."
            )
        if is_already_active_in_semester:
            raise AlreadyEnrolledException(
                f"Estudante '{student.name}' já possui matrícula ativa na disciplina '{course.title}' neste semestre."
            )

        # 2. Validação rigorosa de pré-requisitos obrigatórios
        missing_prereqs = [
            req_id for req_id in course.prerequisite_ids
            if not student.has_completed(req_id)
        ]
        if missing_prereqs:
            raise PrerequisiteNotMetException(
                f"Estudante não cumpriu os pré-requisitos necessários para '{course.title}': "
                f"Pendências: {', '.join(missing_prereqs)}."
            )

        # 3. Limite semestral de créditos
        if not student.can_add_credits(course.credits):
            max_c = student.max_semester_credits
            curr_c = student.current_enrolled_credits
            raise CreditLimitExceededException(
                f"Carga horária pretendida ultrapassa o teto semestral de {max_c} créditos. "
                f"Atual: {curr_c} créditos + Disciplina: {course.credits} créditos > Limite: {max_c}."
            )

        # 4. Verificação de vagas e lotação de turma
        if course.is_full:
            return EnrollmentDecision(
                is_eligible=True,
                status=EnrollmentStatus.WAITLISTED,
                assigned_credits=0,
                reason="Turma regular com vagas esgotadas. Estudante posicionado na fila de espera."
            )

        return EnrollmentDecision(
            is_eligible=True,
            status=EnrollmentStatus.CONFIRMED,
            assigned_credits=course.credits,
            reason="Matrícula aprovada e confirmada com sucesso em vaga regular."
        )
