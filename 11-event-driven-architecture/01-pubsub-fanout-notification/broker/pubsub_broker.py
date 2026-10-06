"""Pub/Sub Broker com suporte a Tópicos e Fan-out de Mensagens."""

from typing import Dict, List, Callable, Any


class PubSubBroker:
    """Broker de mensageria leve simulando topologia de tópicos Fan-out (SNS / Kafka)."""

    def __init__(self) -> None:
        # Mapeamento: topic_name -> lista de consumidores inscritos
        self._topics: Dict[str, List[Callable[[Any], None]]] = {}
        self.published_messages_count: int = 0
        self.total_dispatches_count: int = 0

    def subscribe(self, topic: str, consumer: Callable[[Any], None]) -> None:
        t_name = topic.lower()
        if t_name not in self._topics:
            self._topics[t_name] = []
        self._topics[t_name].append(consumer)

    def publish(self, topic: str, message: Any) -> int:
        """Dispara a mensagem para todos os assinantes do tópico (Fan-out)."""
        t_name = topic.lower()
        subscribers = self._topics.get(t_name, [])
        self.published_messages_count += 1

        successful_deliveries = 0
        for sub in subscribers:
            try:
                sub(message)
                successful_deliveries += 1
                self.total_dispatches_count += 1
            except Exception as exc:
                print(f"[BROKER-WARNING] Falha na entrega para consumidor no tópico '{topic}': {exc}")

        return successful_deliveries
