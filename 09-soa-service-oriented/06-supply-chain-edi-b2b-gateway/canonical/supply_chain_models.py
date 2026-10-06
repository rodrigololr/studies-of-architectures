"""Canonical Data Model (CDM) - Modelo Canônico de Logística e Despacho B2B."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class DespatchLineItem:
    line_number: int
    part_number: str
    description: str
    quantity: int
    unit_of_measure: str  # ex: "PCE" (Peças), "KGM" (Quilos)


@dataclass(frozen=True)
class CanonicalDespatchAdvice:
    """Aviso de Embarque Canônico (Advanced Shipping Notice - ASN / DESADV)."""
    document_id: str
    despatch_date: str
    buyer_code: str
    supplier_code: str
    items: List[DespatchLineItem]


@dataclass(frozen=True)
class IngestionResult:
    is_success: bool
    document_id: str
    assigned_warehouse: Optional[str]
    erp_receipt_id: Optional[str]
    error_message: Optional[str] = None
    edifact_acknowledgement: Optional[str] = None
