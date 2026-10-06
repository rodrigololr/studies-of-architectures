"""
geo_ip_filter.py - Filtro 3: Enriquecimento de Geolocalização por IP.

Consulta tabela de IPs para enriquecer o log com país e cidade de origem.
"""

from __future__ import annotations
from typing import Dict, Optional
from pipeline.base import Filter
from pipeline.context import LogEvent, GeoLocation


class GeoIpFilter(Filter[LogEvent, LogEvent]):
    def __init__(self, ip_database: Dict[str, GeoLocation]) -> None:
        self.ip_database = ip_database

    def process(self, event: LogEvent) -> Optional[LogEvent]:
        if not event.is_valid:
            return event

        geo = self.ip_database.get(event.client_ip)
        if geo:
            event.geo = geo
        else:
            event.geo = GeoLocation(country="Brasil", city="São Paulo")  # Fallback padrão

        return event
