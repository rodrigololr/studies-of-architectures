"""
google_cloud_storage_adapter.py - Adaptador Secundário para Google Cloud Storage (GCS).
"""

from __future__ import annotations
from typing import Dict
from domain.models import StorageProviderType
from ports.driven import BlobStoragePort


class GoogleCloudStorageAdapter(BlobStoragePort):
    def __init__(self, bucket_name: str, project_id: str = "prod-corp-gcp") -> None:
        self.bucket_name = bucket_name
        self.project_id = project_id
        self._gcs_blobs: Dict[str, bytes] = {}

    @property
    def provider_type(self) -> StorageProviderType:
        return StorageProviderType.GOOGLE_CLOUD_STORAGE

    def store_bytes(self, destination_path: str, data: bytes, mime_type: str) -> str:
        gs_uri = f"gs://{self.bucket_name}/{destination_path}"
        self._gcs_blobs[gs_uri] = data
        return gs_uri

    def retrieve_bytes(self, destination_path: str) -> bytes:
        if destination_path in self._gcs_blobs:
            return self._gcs_blobs[destination_path]
        raise FileNotFoundError(f"Blob GCS não encontrado: {destination_path}")

    def delete(self, destination_path: str) -> bool:
        return self._gcs_blobs.pop(destination_path, None) is not None
