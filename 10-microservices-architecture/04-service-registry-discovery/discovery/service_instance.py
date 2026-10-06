"""Service Instance Metadata and Health Status."""

import time
from dataclasses import dataclass, field
from enum import Enum


class InstanceStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    STARTING = "STARTING"


@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    status: InstanceStatus = InstanceStatus.UP
    last_heartbeat_timestamp: float = field(default_factory=time.time)

    @property
    def endpoint_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def update_heartbeat(self) -> None:
        self.last_heartbeat_timestamp = time.time()
