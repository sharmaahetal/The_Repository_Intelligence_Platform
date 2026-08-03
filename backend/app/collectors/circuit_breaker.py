import enum
import time
from collections.abc import Callable
from typing import Any, TypeVar

from backend.app.collectors.exceptions import CircuitBreakerOpenError
from backend.app.logging import logger

T = TypeVar("T")


class CircuitState(enum.StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Circuit Breaker state machine protecting services from hammering failing upstream APIs."""

    def __init__(
        self,
        name: str = "github_api",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_state_change: float = time.perf_counter()

    def _check_state_transition(self) -> None:
        if self.state == CircuitState.OPEN:
            elapsed = time.perf_counter() - self.last_state_change
            if elapsed >= self.recovery_timeout:
                logger.info(
                    f"Circuit Breaker [{self.name}] recovery timeout elapsed -> entering HALF_OPEN state"
                )
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.perf_counter()

    def record_success(self) -> None:
        """Records a successful request, resetting failure count and transitioning to CLOSED state."""
        if self.state != CircuitState.CLOSED:
            logger.info(f"Circuit Breaker [{self.name}] probe succeeded -> resetting to CLOSED state")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.perf_counter()

    def record_failure(self) -> None:
        """Records a failed request, incrementing failure count and tripping to OPEN if threshold exceeded."""
        self.failure_count += 1
        logger.warning(
            f"Circuit Breaker [{self.name}] recorded failure ({self.failure_count}/{self.failure_threshold})",
            extra={"circuit_state": self.state, "failure_count": self.failure_count},
        )
        if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            logger.error(f"Circuit Breaker [{self.name}] TRIPPED -> entering OPEN state")
            self.state = CircuitState.OPEN
            self.last_state_change = time.perf_counter()

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Executes function within circuit breaker protection boundary."""
        self._check_state_transition()

        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit Breaker '{self.name}' is OPEN. Request rejected to protect service and upstream API."
            )

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as exc:
            # Check if exception represents an upstream server failure or network error
            from backend.app.collectors.exceptions import NetworkError
            if isinstance(exc, NetworkError) or getattr(exc, "status_code", 500) in (500, 502, 503, 504):
                self.record_failure()
            raise
