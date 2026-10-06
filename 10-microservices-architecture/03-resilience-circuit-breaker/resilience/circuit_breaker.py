"""Circuit Breaker Pattern (Resilience & Fail-Fast State Machine)."""

import time
from enum import Enum
from typing import Callable, Any, TypeVar, Generic, Optional

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "CLOSED"        # Operação normal: requisições passam
    OPEN = "OPEN"            # Curto-circuito: requisições barradas imediatamente (Fail-Fast)
    HALF_OPEN = "HALF_OPEN"  # Teste de recuperação: permite chamadas controladas


class CircuitBreakerOpenException(Exception):
    """Exceção lançada imediatamente quando o circuito está aberto."""
    pass


class CircuitBreaker:
    """Implementação canônica do Circuit Breaker (Hystrix / Resilience4j)."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 1.0,
        success_threshold: int = 1,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.success_threshold = success_threshold

        self._state: CircuitState = CircuitState.CLOSED
        self._consecutive_failures: int = 0
        self._consecutive_successes: int = 0
        self._last_state_change: float = time.time()

        # Métricas de telemetria
        self.total_calls: int = 0
        self.successful_calls: int = 0
        self.failed_calls: int = 0
        self.short_circuited_calls: int = 0

    @property
    def state(self) -> CircuitState:
        # Avalia transição automática de OPEN para HALF_OPEN com base no tempo decorrido
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_state_change
            if elapsed >= self.recovery_timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Executa a função protegida pelo Circuit Breaker."""
        current_state = self.state

        if current_state == CircuitState.OPEN:
            self.short_circuited_calls += 1
            raise CircuitBreakerOpenException(
                f"Circuito '{self.name}' está ABERTO (OPEN). Chamada rejeitada imediatamente para evitar cascata."
            )

        self.total_calls += 1
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise exc

    def _on_success(self) -> None:
        self.successful_calls += 1
        if self._state == CircuitState.HALF_OPEN:
            self._consecutive_successes += 1
            if self._consecutive_successes >= self.success_threshold:
                # Serviço se recuperou: fecha o circuito
                self._transition_to(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            self._consecutive_failures = 0

    def _on_failure(self) -> None:
        self.failed_calls += 1
        if self._state == CircuitState.HALF_OPEN:
            # Falha durante teste: reabre imediatamente
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self.failure_threshold:
                # Atingiu o limite de tolerância: abre o circuito
                self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        self._state = new_state
        self._last_state_change = time.time()
        self._consecutive_failures = 0
        self._consecutive_successes = 0
