"""Catálogo de Serviços Corporativos e Governança SOA (Service Registry & Directory)."""

from dataclasses import dataclass
from typing import Dict, Set, Optional


@dataclass(frozen=True)
class ServiceMetadata:
    service_id: str
    service_name: str
    authority_organ: str
    endpoint_uri: str
    required_clearance_roles: Set[str]


class ServiceRegistry:
    """Repositório central de descoberta e governança de serviços do barramento."""

    def __init__(self) -> None:
        self._services: Dict[str, ServiceMetadata] = {}
        self._consumer_roles: Dict[str, Set[str]] = {}

        self._register_default_services()
        self._register_default_consumers()

    def _register_default_services(self) -> None:
        self.register_service(
            ServiceMetadata(
                service_id="SVC_RECEITA_CPF",
                service_name="Consulta Base Nacional CPF",
                authority_organ="Receita Federal do Brasil",
                endpoint_uri="urn:gov:rfb:cpf:v2",
                required_clearance_roles={"BASIC_CITIZEN_READ", "FULL_ACCESS"},
            )
        )
        self.register_service(
            ServiceMetadata(
                service_id="SVC_DETRAN_CNH",
                service_name="Consulta Habilitação e Trânsito",
                authority_organ="DETRAN Nacional",
                endpoint_uri="urn:gov:detran:cnh:v1",
                required_clearance_roles={"TRAFFIC_SECURITY", "FULL_ACCESS"},
            )
        )
        self.register_service(
            ServiceMetadata(
                service_id="SVC_CARTORIO_CIVIL",
                service_name="Consulta Registro Civil e Matrículas",
                authority_organ="Associação dos Registradores Civis",
                endpoint_uri="urn:gov:cartorio:civil:v1",
                required_clearance_roles={"LEGAL_JUSTICE", "FULL_ACCESS"},
            )
        )

    def _register_default_consumers(self) -> None:
        # Perfis de órgãos públicos autorizados a consumir o barramento
        self._consumer_roles["PREFEITURA_CAMPINAS"] = {"BASIC_CITIZEN_READ"}
        self._consumer_roles["POLICIA_RODOVIARIA"] = {"BASIC_CITIZEN_READ", "TRAFFIC_SECURITY"}
        self._consumer_roles["MINISTERIO_PUBLICO"] = {"FULL_ACCESS"}

    def register_service(self, meta: ServiceMetadata) -> None:
        self._services[meta.service_id] = meta

    def get_service(self, service_id: str) -> Optional[ServiceMetadata]:
        return self._services.get(service_id)

    def is_authorized(self, consumer_id: str, service_id: str) -> bool:
        roles = self._consumer_roles.get(consumer_id, set())
        meta = self._services.get(service_id)
        if not meta:
            return False
        return bool(roles.intersection(meta.required_clearance_roles))
