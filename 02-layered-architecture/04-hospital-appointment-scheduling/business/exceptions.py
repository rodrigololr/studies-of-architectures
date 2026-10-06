"""
exceptions.py - Camada de Negócio (Business Layer).
Exceções relacionadas a conflitos de agenda e regras hospitalares.
"""


class BusinessException(Exception):
    pass


class ScheduleConflictException(BusinessException):
    pass


class PastDateException(BusinessException):
    pass


class AppointmentNotFoundException(BusinessException):
    pass


class InvalidAppointmentStateException(BusinessException):
    pass
