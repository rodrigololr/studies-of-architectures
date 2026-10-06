"""Implementações em memória dos repositórios acadêmicos (Ring 4 - Infrastructure)."""

from typing import Dict, Optional, List
from domain.model.student import Student
from domain.model.course import Course
from domain.model.enrollment import Enrollment, EnrollmentStatus
from application.interfaces import (
    IStudentRepository,
    ICourseRepository,
    IEnrollmentRepository,
)


class InMemoryStudentRepository(IStudentRepository):
    """Repositório em memória de alunos."""
    def __init__(self, students: Optional[Dict[str, Student]] = None) -> None:
        self._students: Dict[str, Student] = students or {}

    def get_by_id(self, student_id: str) -> Optional[Student]:
        return self._students.get(student_id)

    def save(self, student: Student) -> None:
        self._students[student.student_id] = student


class InMemoryCourseRepository(ICourseRepository):
    """Repositório em memória de cursos e disciplinas."""
    def __init__(self, courses: Optional[Dict[str, Course]] = None) -> None:
        self._courses: Dict[str, Course] = courses or {}

    def get_by_id(self, course_id: str) -> Optional[Course]:
        return self._courses.get(course_id)

    def save(self, course: Course) -> None:
        self._courses[course.course_id] = course


class InMemoryEnrollmentRepository(IEnrollmentRepository):
    """Repositório em memória de matrículas."""
    def __init__(self) -> None:
        self._enrollments: Dict[str, Enrollment] = {}

    def get_by_id(self, enrollment_id: str) -> Optional[Enrollment]:
        return self._enrollments.get(enrollment_id)

    def save(self, enrollment: Enrollment) -> None:
        self._enrollments[enrollment.enrollment_id] = enrollment

    def find_active(self, student_id: str, course_id: str, semester: str) -> Optional[Enrollment]:
        for e in self._enrollments.values():
            if (
                e.student_id == student_id
                and e.course_id == course_id
                and e.semester == semester
                and e.status in [EnrollmentStatus.CONFIRMED, EnrollmentStatus.WAITLISTED]
            ):
                return e
        return None

    def list_by_student(self, student_id: str) -> List[Enrollment]:
        return [e for e in self._enrollments.values() if e.student_id == student_id]
