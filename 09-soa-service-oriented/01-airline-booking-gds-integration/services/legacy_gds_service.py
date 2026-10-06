"""Serviço Legado: Global Distribution System (GDS Amadeus / Sabre Simulator).

Sistemas GDS operam com mensagens de texto plano de formato proprietário (simulando
teleprocessamento de mainframe e EDIFACT). O serviço não conhece JSON nem REST.
"""

import uuid
from typing import Dict


class LegacyGdsService:
    """Serviço Legado autônomo participante da infraestrutura SOA."""
    def __init__(self) -> None:
        # Estado de PNRs retidos no inventário da distribuição aérea
        self._active_pnrs: Dict[str, str] = {}

    def execute_terminal_command(self, raw_command: str) -> str:
        """Processa comando de terminal legado tipo TTY/EDIFACT."""
        # Formato esperado: "HOLD|FLT:LA3301|DATE:2026-11-20|PAX:SILVA/JOSE"
        if raw_command.startswith("HOLD|"):
            pnr = uuid.uuid4().hex[:6].upper()
            self._active_pnrs[pnr] = raw_command
            return f"RESP:OK|PNR:{pnr}|STATUS:HOLD_CONFIRMED|TTL:15MIN"

        # Formato de cancelamento: "CANCEL|PNR:ABC123"
        if raw_command.startswith("CANCEL|"):
            parts = dict(p.split(":") for p in raw_command.split("|") if ":" in p)
            pnr = parts.get("PNR")
            if pnr in self._active_pnrs:
                del self._active_pnrs[pnr]
                return f"RESP:OK|PNR:{pnr}|STATUS:RELEASED_VOID"
            return "RESP:ERR|CODE:PNR_NOT_FOUND"

        return "RESP:ERR|CODE:INVALID_COMMAND"
