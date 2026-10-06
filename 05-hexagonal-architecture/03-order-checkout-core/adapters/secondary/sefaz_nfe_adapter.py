"""
sefaz_nfe_adapter.py - Adaptador Secundário de Emissão de Nota Fiscal (SEFAZ).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.models import Order, InvoiceDetails
from ports.driven import FiscalInvoicePort


class SefazNfeAdapter(FiscalInvoicePort):
    def __init__(self, cnpj_emissor: str) -> None:
        self.cnpj_emissor = cnpj_emissor
        self._current_nfe_seq = 1000

    def issue_invoice(self, order: Order) -> InvoiceDetails:
        self._current_nfe_seq += 1
        nfe_num = f"NFE-{self._current_nfe_seq:06d}"
        key = f"3526{self.cnpj_emissor}{uuid.uuid4().hex[:20]}"
        return InvoiceDetails(
            invoice_number=nfe_num,
            fiscal_key=key,
            issued_at=datetime.now(timezone.utc),
        )
