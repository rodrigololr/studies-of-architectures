"""OrderServiceClient consumindo instâncias descobertas via Registry e Load Balancer."""

from typing import Dict, Any
from discovery.load_balancer import RoundRobinLoadBalancer


class OrderServiceClient:
    """Cliente de microsserviço com descoberta dinâmica e balanceamento local."""

    def __init__(self, payment_balancer: RoundRobinLoadBalancer) -> None:
        self._balancer = payment_balancer

    def invoke_payment_service(self, order_id: str, amount: float) -> Dict[str, Any]:
        # 1. Seleciona dinamicamente a instância da vez pelo Round-Robin
        instance = self._balancer.select_instance()

        # 2. Simula chamada HTTP à instância selecionada
        return {
            "order_id": order_id,
            "status": "PROCESSED",
            "served_by_instance": instance.instance_id,
            "endpoint_target": instance.endpoint_url,
            "amount": amount,
        }
