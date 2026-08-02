import asyncio
import time
from typing import Any

from backend.app.logging import logger


class RateLimiter:
    """Standalone rate limit monitor tracking upstream quota headers and handling rate limit backoff."""

    def __init__(self, buffer_seconds: int = 1) -> None:
        self.buffer_seconds = buffer_seconds
        self.remaining: int | None = None
        self.reset_timestamp: int | None = None

    def update_from_headers(self, headers: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
        """Parses rate limit metadata from HTTP headers and updates current state."""
        headers_lower = {k.lower(): str(v) for k, v in headers.items()}

        remaining = None
        if "x-ratelimit-remaining" in headers_lower and headers_lower["x-ratelimit-remaining"].isdigit():
            remaining = int(headers_lower["x-ratelimit-remaining"])
            self.remaining = remaining

        reset_time = None
        if "x-ratelimit-reset" in headers_lower and headers_lower["x-ratelimit-reset"].isdigit():
            reset_time = int(headers_lower["x-ratelimit-reset"])
            self.reset_timestamp = reset_time

        retry_after = None
        if "retry-after" in headers_lower and headers_lower["retry-after"].isdigit():
            retry_after = int(headers_lower["retry-after"])

        return remaining, reset_time, retry_after

    async def wait_if_needed(self, retry_after: int | None = None) -> float:
        """Enforces rate limit backoff sleep if Retry-After header is present or remaining quota is 0."""
        if retry_after is not None and retry_after > 0:
            logger.warning(
                "Rate limit Retry-After header detected; executing backoff sleep",
                extra={"sleep_seconds": retry_after},
            )
            await asyncio.sleep(retry_after)
            return float(retry_after)

        if self.remaining == 0 and self.reset_timestamp is not None:
            now = int(time.time())
            diff = self.reset_timestamp - now
            if diff > 0:
                sleep_seconds = float(diff + self.buffer_seconds)
                logger.warning(
                    "GitHub API rate limit depleted; waiting for reset window",
                    extra={"reset_timestamp": self.reset_timestamp, "sleep_seconds": sleep_seconds},
                )
                await asyncio.sleep(sleep_seconds)
                return sleep_seconds

        return 0.0
