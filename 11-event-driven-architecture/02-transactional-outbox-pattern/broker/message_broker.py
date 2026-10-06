"""Simulador de Message Broker Externo (Kafka / RabbitMQ) com controle de saúde."""

from typing import List, Dict, Any


class ExternalMessageBroker:
    """Broker de mensageria externo sujeito a indisponibilidades temporárias de rede."""

    def __init__(self) -> None:
        self.is_alive: bool = True
        self.delivered_events: List[Dict[str, Any]] = []

    def publish(self, topic: str, payload: Dict[str, Any]) -> bool:
        if not self.is_alive:
            raise ConnectionError(
                f"Falha de conexão com o Message Broker no tópico '{topic}': Broker inacessível."
            )
        self.delivered_events.append({"topic": topic, "payload": payload})
        return True
