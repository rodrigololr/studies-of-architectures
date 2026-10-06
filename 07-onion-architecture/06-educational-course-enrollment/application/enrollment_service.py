"""Application Service: Casos de uso de matrícula e trancamento acadêmico."""

import uuid
from domain.model.enrollment import Enrollment, EnrollmentStatus
from domain.model.exceptions import AcademicDomainException
from domain.services.enrollment_validator import EnrollmentEligibilityDomainService
from application.interfaces import (
    IStudentRepository,
    ICourseRepository,
    IEnrollmentRepository,
    IAcademicNotificationGateway,
)
from application.dtos import (
    EnrollStudentCommand,
    EnrollStudentResponseDto,
    DropEnrollmentCommand,
    DropEnrollmentResponseDto,
)


class AcademicEnrollmentApplicationService:
    """Serviço da Aplicação (Ring 3 da Onion Architecture).
    
    Orquestra fluxo de admissão curricular, valida elegibilidade via Domain Service
    e atualiza o estado acadêmico do aluno e da turma.
    """

    def __init__(
        self,
        student_repo: IStudentRepository,
        course_repo: ICourseRepository,
        enrollment_repo: IEnrollmentRepository,
        notification_gateway: IAcademicNotificationGateway,
        eligibility_service: EnrollmentEligibilityDomainService,
    ) -> None:
        self._student_repo = student_repo
        self._course_repo = course_repo
        self._enrollment_repo = enrollment_repo
        self._notification_gateway = notification_gateway
        self._eligibility_service = eligibility_service

    def enroll(self, cmd: EnrollStudentCommand) -> EnrollStudentResponseDto:
        """Processa pedido de matrícula em disciplina."""
        student = self._student_repo.get_by_id(cmd.student_id)
        if not student:
            raise AcademicDomainException(f"Estudante ID '{cmd.student_id}' não localizado.")

        course = self._course_repo.get_by_id(cmd.course_id)
        if not course:
            raise AcademicDomainException(f"Disciplina ID '{cmd.course_id}' não localizada.")

        active_enrollment = self._enrollment_repo.find_active(
            student_id=student.student_id,
            course_id=course.course_id,
            semester=cmd.semester,
        )

        # Avaliação de regras puras no Domain Service (Ring 2)
        decision = self._eligibility_service.evaluate_eligibility(
            student=student,
            course=course,
            is_already_active_in_semester=active_enrollment is not None,
        )

        enrollment_id = f"ENR_{uuid.uuid4().hex[:8].upper()}"
        enrollment = Enrollment(
            enrollment_id=enrollment_id,
            student_id=student.student_id,
            course_id=course.course_id,
            semester=cmd.semester,
            credits=course.credits,
            status=decision.status,
        )

        if decision.status == EnrollmentStatus.CONFIRMED:
            student.add_credits(course.credits)
            course.increment_enrolled()
        elif decision.status == EnrollmentStatus.WAITLISTED:
            course.increment_waitlist()

        # Persistência atômica nos repositórios
        self._enrollment_repo.save(enrollment)
        self._student_repo.save(student)
        self._course_repo.save(course)

        # Emissão de notificação
        msg = f"Matrícula em '{course.title}' ({cmd.semester}): {decision.status.value}. {decision.reason}"
        self._notification_gateway.send_notification(student.name, msg)

        return EnrollStudentResponseDto(
            enrollment_id=enrollment_id,
            student_name=student.name,
            course_title=course.title,
            status=decision.status.value,
            credits_assigned=decision.assigned_credits,
            current_total_credits=student.current_enrolled_credits,
            message=decision.reason,
        )

    def drop_course(self, cmd: DropEnrollmentCommand) -> DropEnrollmentResponseDto:
        """Tranca/cancela a matrícula ativa de um aluno em disciplina."""
        enrollment = self._enrollment_repo.get_by_id(cmd.enrollment_id)
        if not enrollment:
            raise AcademicDomainException(f"Matrícula #{cmd.enrollment_id} não encontrada.")

        if enrollment.status != EnrollmentStatus.CONFIRMED:
            raise AcademicDomainException("Apenas matrículas ativas/confirmadas podem ser trancadas.")

        student = self._student_repo.get_by_id(enrollment.student_id)
        course = self._course_repo.get_by_id(enrollment.course_id)

        # Libera os créditos e as vagas
        credits_to_release = enrollment.credits
        enrollment.drop()
        if student:
            student.remove_credits(credits_to_release)
            self._student_repo.save(student)
        if course:
            course.decrement_enrolled()
            self._course_repo.save(course)

        self._enrollment_repo.save(enrollment)

        if student and course:
            self._notification_gateway.send_notification(
                student.name,
                f"Trancamento confirmado da disciplina '{course.title}'. {credits_to_release} créditos liberados."
            )

        return DropEnrollmentResponseDto(
            enrollment_id=enrollment.enrollment_id,
            status=enrollment.status.value,
            credits_released=credits_to_release,
            current_total_credits=student.current_enrolled_credits if student else 0,
            message="Disciplina trancada com sucesso e créditos liberados.",
        )
