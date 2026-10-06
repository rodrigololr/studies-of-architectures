"""Service Registry Corporativo para Provisionamento de Telecom."""

from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass(frozen=True)
class TelecomServiceMetadata:
    service_name: str
    version: str
    protocol: str
    description: str
    instance: Any


class TelecomServiceRegistry:
    def __init__(self) -> None:
        self._services: Dict[str, TelecomServiceMetadata] = {}

    def register(self, name: str, version: str, protocol: str, desc: str, instance: Any) -> None:
        self._services[name] = TelecomServiceMetadata(name, version, protocol, desc, instance)

    def lookup(self, name: str) -> Optional[TelecomServiceMetadata]:
        return self._services.get(name)

    def list_all(self) -> Dict[str, TelecomServiceMetadata]:
        return dict(self._services)
