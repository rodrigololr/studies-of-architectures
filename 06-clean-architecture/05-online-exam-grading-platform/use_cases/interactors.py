"""
use_cases/interactors.py - Camada 2: Interactor de Correção de Provas e Emissão de Certificados.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from entities.models import Certificate
from use_cases.dto import SubmitExamRequestModel, SubmitExamResponseModel
from use_cases.boundaries import (
    GradeExamInputBoundary,
    GradeExamOutputBoundary,
    ExamRepositoryGateway,
    StudentRepositoryGateway,
    CertificateRepositoryGateway,
)


class GradeExamInteractor(GradeExamInputBoundary):
    def __init__(
        self,
        exam_repo: ExamRepositoryGateway,
        student_repo: StudentRepositoryGateway,
        certificate_repo: CertificateRepositoryGateway,
        presenter: GradeExamOutputBoundary,
    ) -> None:
        self.exam_repo = exam_repo
        self.student_repo = student_repo
        self.certificate_repo = certificate_repo
        self.presenter = presenter

    def execute(self, request: SubmitExamRequestModel) -> None:
        # 1. Localiza o Exame
        exam = self.exam_repo.find_by_id(request.exam_id)
        if not exam:
            self.presenter.present(SubmitExamResponseModel(
                success=False,
                student_name=None,
                exam_title=None,
                score_obtained=0.0,
                total_points=0.0,
                score_percentage=0.0,
                is_passed=False,
                certificate_id=None,
                message=f"Exame '{request.exam_id}' não localizado no sistema.",
            ))
            return

        # 2. Localiza o Aluno
        student = self.student_repo.find_by_id(request.student_id)
        if not student:
            self.presenter.present(SubmitExamResponseModel(
                success=False,
                student_name=None,
                exam_title=exam.title,
                score_obtained=0.0,
                total_points=0.0,
                score_percentage=0.0,
                is_passed=False,
                certificate_id=None,
                message=f"Estudante '{request.student_id}' não cadastrado.",
            ))
            return

        # 3. Invoca a Regra Corporativa de Avaliação Ponderada na Entidade
        score, total, percentage, is_passed = exam.evaluate_submission(request.answers)

        certificate_id = None
        if is_passed:
            # Emissão do Certificado Oficial
            certificate_id = f"CERT_{uuid.uuid4().hex[:10].upper()}"
            certificate = Certificate(
                certificate_id=certificate_id,
                student_id=student.student_id,
                student_name=student.name,
                exam_id=exam.exam_id,
                exam_title=exam.title,
                score_percent=percentage,
                issued_at=datetime.now(timezone.utc),
            )
            self.certificate_repo.save(certificate)
            message = (
                f"Parabéns {student.name}! Você atingiu {percentage:.1f}% e foi APROVADO "
                f"(Mínimo exigido: {exam.min_passing_percent:.1f}%). Certificado emitido."
            )
        else:
            message = (
                f"Aproveitamento de {percentage:.1f}% insuficiente para aprovação "
                f"(Mínimo exigido: {exam.min_passing_percent:.1f}%)."
            )

        # 4. Apresentação (Output Boundary)
        self.presenter.present(SubmitExamResponseModel(
            success=True,
            student_name=student.name,
            exam_title=exam.title,
            score_obtained=score,
            total_points=total,
            score_percentage=percentage,
            is_passed=is_passed,
            certificate_id=certificate_id,
            message=message,
        ))
