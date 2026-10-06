"""Client-Side Load Balancer (Round-Robin / Netflix Ribbon Pattern)."""

from typing import Optional, List
from discovery.service_instance import ServiceInstance
from discovery.service_registry import ServiceRegistry


class NoAvailableInstanceException(Exception):
    pass


class RoundRobinLoadBalancer:
    """Balanceador de carga no lado do cliente que consome o Service Registry."""

    def __init__(self, registry: ServiceRegistry, target_service_name: str) -> None:
        self.registry = registry
        self.target_service_name = target_service_name.upper()
        self._current_index: int = 0

    def select_instance(self) -> ServiceInstance:
        instances = self.registry.get_healthy_instances(self.target_service_name)
        if not instances:
            raise NoAvailableInstanceException(
                f"Nenhuma instância saudável encontrada no Registry para '{self.target_service_name}'."
            )

        # Ordena por instance_id para garantir determinação no anel Round-Robin
        sorted_instances = sorted(instances, key=lambda i: i.instance_id)

        selected = sorted_instances[self._current_index % len(sorted_instances)]
        self._current_index += 1
        return selected
