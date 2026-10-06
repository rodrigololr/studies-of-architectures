"""Implementação Interna do Módulo Compliance (Schema: compliance)."""

from typing import Set


class _InternalComplianceRepository:
    def __init__(self) -> None:
        self._blacklisted_keys: Set[str] = set()

    def add_blacklisted_key(self, pix_key: str) -> None:
        self._blacklisted_keys.add(pix_key.lower().strip())

    def is_blacklisted(self, pix_key: str) -> bool:
        return pix_key.lower().strip() in self._blacklisted_keys
