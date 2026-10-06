"""
client.py - Cliente Resolvedor DNS com Cache em Memória e expiração por TTL.

Consulta primeiramente o cache local; somente em caso de cache miss ou TTL expirado
dispara uma requisição UDP para o servidor remoto.
"""

from __future__ import annotations
from dataclasses import dataclass
import random
import socket
import time
from typing import Dict, Optional, Tuple
from protocol import DnsQuery, DnsResponse, QueryType


@dataclass
class CacheEntry:
    ip: str
    expires_at: float

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class DnsClient:
    def __init__(self, server_host: str, server_port: int, timeout_sec: float = 2.0) -> None:
        self.server_host = server_host
        self.server_port = server_port
        self.timeout_sec = timeout_sec
        self._cache: Dict[str, CacheEntry] = {}

    def resolve(self, domain: str) -> Tuple[Optional[str], str]:
        """
        Resolve o domínio para um IP.
        Retorna (ip, fonte: 'CACHE_HIT' | 'NETWORK_QUERY' | 'NOT_FOUND').
        """
        normalized_domain = domain.lower().strip()

        # 1. Verifica Cache Local
        if normalized_domain in self._cache:
            entry = self._cache[normalized_domain]
            if not entry.is_expired:
                return entry.ip, "CACHE_HIT"
            # Expirou: remove do cache
            del self._cache[normalized_domain]

        # 2. Faz requisição de rede via UDP
        query_id = random.randint(1000, 9999)
        query = DnsQuery(query_id=query_id, domain=normalized_domain, record_type=QueryType.A)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout_sec)

        try:
            sock.sendto(query.serialize(), (self.server_host, self.server_port))
            data, _ = sock.recvfrom(2048)
            response = DnsResponse.deserialize(data)

            if not response or response.query_id != query_id or not response.found or not response.resolved_ip:
                return None, "NOT_FOUND"

            # Salva no cache com TTL
            expires_at = time.time() + response.ttl_seconds
            self._cache[normalized_domain] = CacheEntry(
                ip=response.resolved_ip, expires_at=expires_at
            )
            return response.resolved_ip, "NETWORK_QUERY"

        except socket.timeout:
            return None, "TIMEOUT"
        finally:
            sock.close()
