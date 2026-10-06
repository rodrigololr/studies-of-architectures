"""Interfaces da camada de aplicação (Onion Architecture)."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.model.student import Student
from domain.model.course import Course
from domain.model.enrollment import Enrollment


class IStudentRepository(ABC):
    """Porta para persistência de dados de estudantes."""
    @abstractmethod
    def get_by_id(self, student_id: str) -> Optional[Student]:
        pass

    @abstractmethod
    def save(self, student: Student) -> None:
        pass


class ICourseRepository(ABC):
    """Porta para persistência de dados de cursos e turmas."""
    @abstractmethod
    def get_by_id(self, course_id: str) -> Optional[Course]:
        pass

    @abstractmethod
    def save(self, course: Course) -> None:
        pass


class IEnrollmentRepository(ABC):
    """Porta para persistência de matrículas acadêmicas."""
    @abstractmethod
    def get_by_id(self, enrollment_id: str) -> Optional[Enrollment]:
        pass

    @abstractmethod
    def save(self, enrollment: Enrollment) -> None:
        pass

    @abstractmethod
    def find_active(self, student_id: str, course_id: str, semester: str) -> Optional[Enrollment]:
        pass

    @abstractmethod
    def list_by_student(self, student_id: str) -> List[Enrollment]:
        pass


class IAcademicNotificationGateway(ABC):
    """Porta para envio de notificações acadêmicas aos alunos."""
    @abstractmethod
    def send_notification(self, student_name: str, message: str) -> None:
        pass
