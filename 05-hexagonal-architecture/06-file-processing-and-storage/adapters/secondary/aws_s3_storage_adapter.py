"""
aws_s3_storage_adapter.py - Adaptador Secundário para AWS S3 Bucket.
"""

from __future__ import annotations
from typing import Dict
from domain.models import StorageProviderType
from ports.driven import BlobStoragePort


class AwsS3StorageAdapter(BlobStoragePort):
    def __init__(self, bucket_name: str, region: str = "us-east-1") -> None:
        self.bucket_name = bucket_name
        self.region = region
        # Armazena bytes em memória simulando as keys do bucket S3
        self._s3_objects: Dict[str, bytes] = {}

    @property
    def provider_type(self) -> StorageProviderType:
        return StorageProviderType.AWS_S3

    def store_bytes(self, destination_path: str, data: bytes, mime_type: str) -> str:
        s3_uri = f"s3://{self.bucket_name}/{destination_path}"
        self._s3_objects[s3_uri] = data
        return s3_uri

    def retrieve_bytes(self, destination_path: str) -> bytes:
        if destination_path in self._s3_objects:
            return self._s3_objects[destination_path]
        raise FileNotFoundError(f"Objeto S3 não encontrado: {destination_path}")

    def delete(self, destination_path: str) -> bool:
        return self._s3_objects.pop(destination_path, None) is not None
