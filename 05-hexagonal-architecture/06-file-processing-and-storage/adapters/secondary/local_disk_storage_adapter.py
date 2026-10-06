"""
local_disk_storage_adapter.py - Adaptador Secundário para Disco Local / NFS.
"""

from __future__ import annotations
from typing import Dict
from domain.models import StorageProviderType
from ports.driven import BlobStoragePort


class LocalDiskStorageAdapter(BlobStoragePort):
    def __init__(self, base_mount_path: str = "/var/data/storage") -> None:
        self.base_mount_path = base_mount_path
        self._disk_files: Dict[str, bytes] = {}

    @property
    def provider_type(self) -> StorageProviderType:
        return StorageProviderType.LOCAL_DISK

    def store_bytes(self, destination_path: str, data: bytes, mime_type: str) -> str:
        full_path = f"{self.base_mount_path}/{destination_path}"
        self._disk_files[full_path] = data
        return full_path

    def retrieve_bytes(self, destination_path: str) -> bytes:
        if destination_path in self._disk_files:
            return self._disk_files[destination_path]
        raise FileNotFoundError(f"Arquivo local não encontrado: {destination_path}")

    def delete(self, destination_path: str) -> bool:
        return self._disk_files.pop(destination_path, None) is not None
