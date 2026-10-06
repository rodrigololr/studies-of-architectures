"""Exceções do domínio acadêmico de matrículas."""

class AcademicDomainException(Exception):
    """Exceção base de regras de negócio acadêmicas."""
    pass


class PrerequisiteNotMetException(AcademicDomainException):
    """Lançada quando o estudante não cumpriu as disciplinas pré-requisito."""
    pass


class CreditLimitExceededException(AcademicDomainException):
    """Lançada quando os créditos pretendidos excedem o teto semestral permitido."""
    pass


class AlreadyEnrolledException(AcademicDomainException):
    """Lançada quando o aluno já está matriculado na disciplina ou já a concluiu."""
    pass


class CourseFullException(AcademicDomainException):
    """Lançada quando as vagas regulares da turma estão esgotadas."""
    pass
