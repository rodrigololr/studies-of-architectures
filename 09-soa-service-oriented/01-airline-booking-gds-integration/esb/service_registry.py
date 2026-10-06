"""Service Registry / UDDI: Catálogo Corporativo de Serviços SOA."""

from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass(frozen=True)
class ServiceMetadata:
    service_name: str
    service_version: str
    endpoint_protocol: str  # "REST", "SOAP", "RAW_TTY_SOCKET"
    description: str
    service_instance: Any


class ServiceRegistry:
    """Repositório de Descobrabilidade de Serviços (Princípio de Discoverability de SOA)."""
    def __init__(self) -> None:
        self._registry: Dict[str, ServiceMetadata] = {}

    def register_service(
        self,
        name: str,
        version: str,
        protocol: str,
        description: str,
        instance: Any,
    ) -> None:
        self._registry[name] = ServiceMetadata(
            service_name=name,
            service_version=version,
            endpoint_protocol=protocol,
            description=description,
            service_instance=instance,
        )

    def lookup(self, name: str) -> Optional[ServiceMetadata]:
        return self._registry.get(name)

    def list_services(self) -> Dict[str, ServiceMetadata]:
        return dict(self._registry)
