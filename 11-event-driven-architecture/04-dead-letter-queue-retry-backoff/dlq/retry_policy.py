"""Retry Policy com Exponential Backoff."""

import math


class RetryPolicy:
    """Calculador de tempo de espera exponencial para retentativas de eventos."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_ms: float = 10.0,
        backoff_multiplier: float = 2.0,
        max_delay_ms: float = 1000.0,
    ) -> None:
        self.max_retries = max_retries
        self.initial_delay_ms = initial_delay_ms
        self.backoff_multiplier = backoff_multiplier
        self.max_delay_ms = max_delay_ms

    def compute_delay_seconds(self, retry_attempt: int) -> float:
        """Calcula o atraso em segundos: delay = min(initial * (multiplier ^ attempt), max_delay)."""
        delay_ms = self.initial_delay_ms * math.pow(self.backoff_multiplier, retry_attempt)
        capped_ms = min(delay_ms, self.max_delay_ms)
        return round(capped_ms / 1000.0, 4)

    def should_retry(self, current_attempt: int) -> bool:
        return current_attempt < self.max_retries
