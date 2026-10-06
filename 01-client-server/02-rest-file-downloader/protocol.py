"""
protocol.py - Protocolo HTTP minimalista para transferência de arquivos em streaming.

Demonstra como o padrão Cliente-Servidor da Web funciona por baixo dos panos:
Requisições com linha de comando, cabeçalhos delimitados por CRLF (\\r\\n)
e corpo de dados binários transmitido em blocos (chunks).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class HttpResponseHeaders:
    status_code: int
    reason: str
    headers: Dict[str, str]

    @property
    def content_length(self) -> int:
        return int(self.headers.get("Content-Length", 0))

    def serialize(self) -> bytes:
        lines = [f"HTTP/1.1 {self.status_code} {self.reason}"]
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        lines.append("")
        return "\r\n".join(lines).encode("latin-1")


def parse_request_line(raw_headers: str) -> Tuple[str, str, Dict[str, str]]:
    """Extrai método, caminho e cabeçalhos de uma requisição HTTP básica."""
    lines = raw_headers.strip().split("\r\n")
    if not lines:
        return "GET", "/", {}

    parts = lines[0].split(" ")
    method = parts[0] if len(parts) > 0 else "GET"
    path = parts[1] if len(parts) > 1 else "/"

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ": " in line:
            key, val = line.split(": ", 1)
            headers[key.strip()] = val.strip()

    return method, path, headers
