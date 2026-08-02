import random
import time
from typing import Any


class RetryPolicy:
    """Centralized, pluggable retry strategy handling backoff, jitter, and retry evaluation."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        retryable_statuses: set[int] | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retryable_statuses = retryable_statuses or {500, 502, 503, 504, 429}

    def should_retry(self, status_code: int | None, attempt: int, exc: Exception | None = None) -> bool:
        """Determines if a request attempt should be retried based on status code and attempt count."""
        if attempt >= self.max_retries:
            return False
        if status_code is not None and status_code in self.retryable_statuses:
            return True
        if exc is not None:
            from backend.app.collectors.exceptions import NetworkError
            if isinstance(exc, NetworkError):
                return True
        return False

    def calculate_backoff(self, attempt: int) -> float:
        """Calculates exponential backoff with full jitter for specified attempt (1-indexed)."""
        backoff = (self.base_delay ** attempt) + random.uniform(0.1, 1.0)
        return min(backoff, self.max_delay)


# Backward-compatible helper functions
def is_retryable_status(status_code: int) -> bool:
    """Return True if HTTP status code is a retryable transient error or rate-limit code (500, 502, 503, 504, 429)."""
    return status_code in (500, 502, 503, 504, 429)


def calculate_exponential_backoff(
    attempt: int, base_delay: float = 2.0, max_delay: float = 60.0
) -> float:
    """Calculate exponential backoff with full jitter for attempt number (1-indexed)."""
    backoff = (base_delay**attempt) + random.uniform(0.1, 1.0)
    return min(backoff, max_delay)


def parse_rate_limit_headers(headers: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    """Extract (remaining, reset_timestamp, retry_after_seconds) from HTTP headers."""
    headers_lower = {k.lower(): str(v) for k, v in headers.items()}

    remaining = None
    if "x-ratelimit-remaining" in headers_lower and headers_lower["x-ratelimit-remaining"].isdigit():
        remaining = int(headers_lower["x-ratelimit-remaining"])

    reset_time = None
    if "x-ratelimit-reset" in headers_lower and headers_lower["x-ratelimit-reset"].isdigit():
        reset_time = int(headers_lower["x-ratelimit-reset"])

    retry_after = None
    if "retry-after" in headers_lower and headers_lower["retry-after"].isdigit():
        retry_after = int(headers_lower["retry-after"])

    return remaining, reset_time, retry_after


def calculate_rate_limit_sleep(reset_timestamp: int | None, buffer_seconds: int = 1) -> float:
    """Calculate seconds to sleep until GitHub rate limit resets."""
    if reset_timestamp is None:
        return 0.0
    now = int(time.time())
    diff = reset_timestamp - now
    return float(max(diff + buffer_seconds, 1))
