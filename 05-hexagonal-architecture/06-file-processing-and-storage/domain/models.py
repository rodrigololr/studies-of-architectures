"""
models.py - Modelos de domínio de processamento e armazenamento de arquivos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class StorageProviderType(str, Enum):
    AWS_S3 = "AWS_S3"
    GOOGLE_CLOUD_STORAGE = "GOOGLE_CLOUD_STORAGE"
    LOCAL_DISK = "LOCAL_DISK"


@dataclass(frozen=True)
class FileUploadCommand:
    filename: str
    content_bytes: bytes
    mime_type: str
    uploaded_by_user_id: str


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    original_filename: str
    storage_path: str
    storage_provider: StorageProviderType
    file_size_bytes: int
    sha256_hash: str
    mime_type: str
    uploaded_by: str
    created_at: datetime
