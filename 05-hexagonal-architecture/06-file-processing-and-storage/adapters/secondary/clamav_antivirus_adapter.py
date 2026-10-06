"""
clamav_antivirus_adapter.py - Adaptador Secundário para Scanner Antivírus (ClamAV / TotalAV).
"""

from __future__ import annotations
from ports.driven import AntivirusScannerPort


class ClamAvAntivirusAdapter(AntivirusScannerPort):
    def __init__(self, signature_db_version: str = "2026.10") -> None:
        self.signature_db_version = signature_db_version
        # Assinatura de teste clássica EICAR ou strings maliciosas simuladas
        self._malicious_signatures = [
            b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
            b"malicious_trojan_payload",
        ]

    def scan_file(self, filename: str, data: bytes) -> tuple[bool, str]:
        for sig in self._malicious_signatures:
            if sig in data:
                return False, f"Assinatura maliciosa detectada: Win32.Trojan.Simulator (Assinatura {self.signature_db_version})"
        return True, "Arquivo limpo. Nenhuma ameaça detectada."
