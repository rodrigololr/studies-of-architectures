"""
driver.py - Portas Primárias / Inbound do processamento de arquivos.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from domain.models import FileUploadCommand, StoredDocument


class UploadDocumentUseCasePort(ABC):
    @abstractmethod
    def upload(self, command: FileUploadCommand) -> StoredDocument:
        """Valida, faz varredura antivírus, calcula hash e armazena o arquivo."""
        pass


class DownloadDocumentUseCasePort(ABC):
    @abstractmethod
    def download(self, document_id: str) -> Tuple[StoredDocument, bytes]:
        """Recupera metadados e os bytes brutos do arquivo armazenado."""
        pass
