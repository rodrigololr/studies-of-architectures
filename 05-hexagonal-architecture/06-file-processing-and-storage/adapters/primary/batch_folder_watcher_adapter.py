"""
batch_folder_watcher_adapter.py - Adaptador Primário de Ingestão em Lote (Folder Watcher / Cron).

Simula um worker que varre diretórios locais ou pools de FTP e despacha arquivos
automaticamente para o núcleo hexagonal.
"""

from __future__ import annotations
from typing import List, Tuple
from domain.models import FileUploadCommand, StoredDocument
from ports.driver import UploadDocumentUseCasePort


class BatchFolderWatcherAdapter:
    def __init__(self, upload_use_case: UploadDocumentUseCasePort) -> None:
        self.upload_use_case = upload_use_case

    def ingest_batch(self, files: List[Tuple[str, bytes, str]], operator_id: str) -> List[str]:
        results = []
        for filename, data, mime in files:
            cmd = FileUploadCommand(
                filename=filename,
                content_bytes=data,
                mime_type=mime,
                uploaded_by_user_id=operator_id,
            )
            try:
                doc = self.upload_use_case.upload(cmd)
                results.append(f"[Watcher OK] {filename} -> {doc.storage_path} (ID: {doc.document_id})")
            except Exception as err:
                results.append(f"[Watcher ERRO] {filename} -> Falha: {err}")
        return results
