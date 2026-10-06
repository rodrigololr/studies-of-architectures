"""
in_memory_metadata_adapter.py - Adaptador Secundário de Banco de Metadados de Documentos.
"""

from __future__ import annotations
from typing import Dict, Optional, List
from domain.models import StoredDocument
from ports.driven import DocumentMetadataRepositoryPort


class InMemoryDocumentMetadataAdapter(DocumentMetadataRepositoryPort):
    def __init__(self) -> None:
        self._records: Dict[str, StoredDocument] = {}

    def save(self, document: StoredDocument) -> None:
        self._records[document.document_id] = document

    def find_by_id(self, document_id: str) -> Optional[StoredDocument]:
        return self._records.get(document_id)

    def list_all(self) -> List[StoredDocument]:
        return list(self._records.values())
