"""Service Registry (Simulador do Netflix Eureka / HashiCorp Consul)."""

import time
from typing import Dict, List, Optional
from discovery.service_instance import ServiceInstance, InstanceStatus


class ServiceRegistry:
    """Repositório dinâmico de instâncias ativas de microsserviços."""

    def __init__(self, default_ttl_seconds: float = 2.0) -> None:
        self.default_ttl = default_ttl_seconds
        # Mapeamento: service_name -> {instance_id -> ServiceInstance}
        self._registry: Dict[str, Dict[str, ServiceInstance]] = {}

    def register(self, instance: ServiceInstance) -> None:
        service_name = instance.service_name.upper()
        if service_name not in self._registry:
            self._registry[service_name] = {}
        instance.update_heartbeat()
        self._registry[service_name][instance.instance_id] = instance

    def deregister(self, service_name: str, instance_id: str) -> bool:
        s_name = service_name.upper()
        if s_name in self._registry and instance_id in self._registry[s_name]:
            del self._registry[s_name][instance_id]
            return True
        return False

    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        s_name = service_name.upper()
        if s_name in self._registry and instance_id in self._registry[s_name]:
            self._registry[s_name][instance_id].update_heartbeat()
            return True
        return False

    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        s_name = service_name.upper()
        if s_name not in self._registry:
            return []
        return [
            inst for inst in self._registry[s_name].values()
            if inst.status == InstanceStatus.UP
        ]

    def evict_dead_instances(self, ttl_seconds: Optional[float] = None) -> List[str]:
        """Expulsa instâncias que não renovaram o heartbeat dentro do limiar de TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = time.time()
        evicted_ids: List[str] = []

        for service_name, instances in self._registry.items():
            to_remove = []
            for inst_id, inst in instances.items():
                if (now - inst.last_heartbeat_timestamp) > ttl:
                    to_remove.append(inst_id)
            for inst_id in to_remove:
                del instances[inst_id]
                evicted_ids.append(inst_id)

        return evicted_ids
