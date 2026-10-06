"""
driven.py - Portas Secundárias / Outbound do processamento de arquivos.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models import StorageProviderType, StoredDocument


class BlobStoragePort(ABC):
    @property
    @abstractmethod
    def provider_type(self) -> StorageProviderType:
        """Tipo de provedor de armazenamento (S3, GCS, Local)."""
        pass

    @abstractmethod
    def store_bytes(self, destination_path: str, data: bytes, mime_type: str) -> str:
        """Grava bytes no destino e retorna a URI/Path definitivo."""
        pass

    @abstractmethod
    def retrieve_bytes(self, destination_path: str) -> bytes:
        """Lê os bytes brutos do arquivo."""
        pass

    @abstractmethod
    def delete(self, destination_path: str) -> bool:
        """Remove o arquivo físico."""
        pass


class AntivirusScannerPort(ABC):
    @abstractmethod
    def scan_file(self, filename: str, data: bytes) -> tuple[bool, str]:
        """Realiza varredura contra malwares. Retorna (is_safe, details)."""
        pass


class DocumentMetadataRepositoryPort(ABC):
    @abstractmethod
    def save(self, document: StoredDocument) -> None:
        """Persiste os metadados do documento."""
        pass

    @abstractmethod
    def find_by_id(self, document_id: str) -> Optional[StoredDocument]:
        """Localiza metadados por ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[StoredDocument]:
        """Lista todos os documentos armazenados."""
        pass
