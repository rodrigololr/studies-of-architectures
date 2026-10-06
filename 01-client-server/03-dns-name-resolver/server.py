"""
server.py - Servidor Autoritativo de Nomes sobre UDP.

Ouve pacotes UDP (SOCK_DGRAM) sem estabelecer conexão de stream,
consulta sua tabela de zonas interna e responde com o IP e TTL.
"""

from __future__ import annotations
import socket
import threading
from typing import Dict, Optional, Tuple
from protocol import DnsQuery, DnsResponse, QueryType


class DnsServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        self.host = host
        self.port = port
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._listen_thread: Optional[threading.Thread] = None

        # Tabela autoritativa: domain -> (ip, ttl)
        self._records: Dict[str, Tuple[str, int]] = {
            "api.pagamentos.com": ("192.168.1.100", 2),   # TTL curto (2s) para demonstração de expiração
            "auth.empresa.com.br": ("192.168.1.101", 60),
            "db.interno.corp": ("10.0.0.50", 120),
        }

    @property
    def bound_port(self) -> int:
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server_socket.bind((self.host, self.port))
        self._is_running = True

        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()

    def _listen_loop(self) -> None:
        while self._is_running and self._server_socket:
            try:
                data, client_addr = self._server_socket.recvfrom(2048)
                query = DnsQuery.deserialize(data)
                if not query:
                    continue

                if query.domain in self._records:
                    ip, ttl = self._records[query.domain]
                    response = DnsResponse(
                        query_id=query.query_id,
                        domain=query.domain,
                        record_type=query.record_type,
                        resolved_ip=ip,
                        ttl_seconds=ttl,
                        found=True,
                    )
                else:
                    response = DnsResponse(
                        query_id=query.query_id,
                        domain=query.domain,
                        record_type=query.record_type,
                        resolved_ip=None,
                        ttl_seconds=0,
                        found=False,
                    )

                self._server_socket.sendto(response.serialize(), client_addr)
            except OSError:
                break

    def stop(self) -> None:
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
