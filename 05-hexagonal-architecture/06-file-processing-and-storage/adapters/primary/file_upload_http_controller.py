"""
file_upload_http_controller.py - Adaptador Primário HTTP REST para Upload e Download.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from domain.models import FileUploadCommand
from domain.exceptions import StorageDomainException
from ports.driver import UploadDocumentUseCasePort, DownloadDocumentUseCasePort


class FileUploadHttpController:
    def __init__(
        self,
        upload_use_case: UploadDocumentUseCasePort,
        download_use_case: DownloadDocumentUseCasePort,
    ) -> None:
        self.upload_use_case = upload_use_case
        self.download_use_case = download_use_case

    def handle_post_file(
        self,
        filename: str,
        content_bytes: bytes,
        mime_type: str,
        user_id: str,
    ) -> Tuple[int, Dict[str, Any]]:
        try:
            cmd = FileUploadCommand(
                filename=filename,
                content_bytes=content_bytes,
                mime_type=mime_type,
                uploaded_by_user_id=user_id,
            )
            doc = self.upload_use_case.upload(cmd)
            return 201, {
                "success": True,
                "document_id": doc.document_id,
                "filename": doc.original_filename,
                "storage_uri": doc.storage_path,
                "provider": doc.storage_provider.value,
                "sha256": doc.sha256_hash,
                "size_bytes": doc.file_size_bytes,
            }
        except StorageDomainException as dom_err:
            return 400, {
                "success": False,
                "error": dom_err.__class__.__name__,
                "detail": str(dom_err),
            }
        except Exception as ex:
            return 500, {
                "success": False,
                "error": "InternalServerError",
                "detail": str(ex),
            }

    def handle_get_file(self, document_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            doc, raw_bytes = self.download_use_case.download(document_id)
            return 200, {
                "success": True,
                "document_id": doc.document_id,
                "filename": doc.original_filename,
                "size_bytes": len(raw_bytes),
                "sha256": doc.sha256_hash,
                "content_preview": raw_bytes[:50].decode("utf-8", errors="replace"),
            }
        except StorageDomainException as dom_err:
            return 404, {
                "success": False,
                "error": dom_err.__class__.__name__,
                "detail": str(dom_err),
            }
