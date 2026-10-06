"""
service.py - Núcleo da Aplicação (Core / Hexágono) para Gestão de Arquivos.
"""

from __future__ import annotations
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Optional
from domain.models import FileUploadCommand, StoredDocument
from domain.exceptions import (
    FileTooLargeException,
    DisallowedFileTypeException,
    MalwareDetectedException,
    DocumentNotFoundException,
)
from ports.driver import UploadDocumentUseCasePort, DownloadDocumentUseCasePort
from ports.driven import (
    BlobStoragePort,
    AntivirusScannerPort,
    DocumentMetadataRepositoryPort,
)


class DocumentManagementService(UploadDocumentUseCasePort, DownloadDocumentUseCasePort):
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".csv"}
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        storage_port: BlobStoragePort,
        antivirus_port: AntivirusScannerPort,
        metadata_repo: DocumentMetadataRepositoryPort,
    ) -> None:
        self.storage_port = storage_port
        self.antivirus_port = antivirus_port
        self.metadata_repo = metadata_repo

    def upload(self, command: FileUploadCommand) -> StoredDocument:
        # 1. Validação de Tamanho
        content_size = len(command.content_bytes)
        if content_size > self.MAX_FILE_SIZE_BYTES:
            raise FileTooLargeException(
                f"Arquivo de {content_size} bytes excede o limite de {self.MAX_FILE_SIZE_BYTES} bytes."
            )

        # 2. Validação de Extensão Permitida
        ext = Path(command.filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise DisallowedFileTypeException(
                f"Extensão '{ext}' não autorizada por política de segurança. Permitidas: {sorted(list(self.ALLOWED_EXTENSIONS))}"
            )

        # 3. Varredura Antivírus (Driven Port)
        is_safe, threat_info = self.antivirus_port.scan_file(command.filename, command.content_bytes)
        if not is_safe:
            raise MalwareDetectedException(f"Ameaça detectada no arquivo '{command.filename}': {threat_info}")

        # 4. Cálculo de Hash SHA-256 para Integridade Criptográfica
        sha256_hash = hashlib.sha256(command.content_bytes).hexdigest()

        # 5. Armazenamento Físico via Provedor de Storage (Driven Port)
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        storage_path = f"uploads/{datetime.now(timezone.utc).strftime('%Y/%m')}/{doc_id}_{command.filename}"
        persisted_uri = self.storage_port.store_bytes(storage_path, command.content_bytes, command.mime_type)

        # 6. Gravação de Metadados (Driven Port)
        document = StoredDocument(
            document_id=doc_id,
            original_filename=command.filename,
            storage_path=persisted_uri,
            storage_provider=self.storage_port.provider_type,
            file_size_bytes=content_size,
            sha256_hash=sha256_hash,
            mime_type=command.mime_type,
            uploaded_by=command.uploaded_by_user_id,
            created_at=datetime.now(timezone.utc),
        )

        self.metadata_repo.save(document)
        return document

    def download(self, document_id: str) -> Tuple[StoredDocument, bytes]:
        document = self.metadata_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Documento com identificador '{document_id}' não encontrado.")

        raw_bytes = self.storage_port.retrieve_bytes(document.storage_path)
        return document, raw_bytes
