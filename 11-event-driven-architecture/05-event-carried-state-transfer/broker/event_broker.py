"""Message Broker leve para publicação de eventos ECST."""

from typing import Dict, List, Callable, Any


class EventBroker:
    def __init__(self) -> None:
        self._topics: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        t = topic.lower()
        if t not in self._topics:
            self._topics[t] = []
        self._topics[t].append(handler)

    def publish(self, topic: str, event: Any) -> None:
        t = topic.lower()
        for handler in self._topics.get(t, []):
            handler(event)
