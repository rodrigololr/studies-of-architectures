"""Adaptador de infraestrutura para notificações acadêmicas (Ring 4)."""

from application.interfaces import IAcademicNotificationGateway


class MockAcademicNotificationGateway(IAcademicNotificationGateway):
    """Adaptador de envio de notificações via Portal do Aluno e E-mail Institucional."""
    def __init__(self) -> None:
        self.notifications = []

    def send_notification(self, student_name: str, message: str) -> None:
        entry = f"[Portal Acadêmico / {student_name}]: {message}"
        self.notifications.append(entry)
