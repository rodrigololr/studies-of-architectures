"""
entities/exceptions.py - Camada 1: Exceções de Provas e Avaliações.
"""

from __future__ import annotations


class ExamEntityException(Exception):
    pass


class InvalidExamConfigurationException(ExamEntityException):
    pass
