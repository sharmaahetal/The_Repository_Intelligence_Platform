import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx

from backend.app.collectors.circuit_breaker import CircuitBreaker
from backend.app.collectors.exceptions import (
    GitHubError,
    NetworkError,
    RateLimitExceeded,
    RepositoryNotFound,
    Unauthorized,
)
from backend.app.collectors.rate_limiter import RateLimiter
from backend.app.collectors.retry import RetryPolicy
from backend.app.config import settings
from backend.app.logging import logger


@dataclass
class GitHubResponse:
    """Wrapper holding raw response payload along with HTTP response metadata."""

    data: dict[str, Any] | list[dict[str, Any]]
    headers: dict[str, str]
    status_code: int
    etag: str | None = None
    last_modified: str | None = None
    rate_limit_remaining: int | None = None
    api_version: str | None = None
    snapshot_time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def is_not_modified(self) -> bool:
        """Return True if HTTP response status is 304 Not Modified."""
        return self.status_code == 304


class GitHubAPIClient:
    """Async HTTP client for GitHub API with connection pooling, RetryPolicy, CircuitBreaker, RateLimiter, and ETags."""

    def __init__(
        self,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        rate_limiter: RateLimiter | None = None,
    ):
        self.token = token or settings.github.token
        self.base_url = settings.github.api_url
        self.timeout = settings.github.request_timeout_seconds
        self._client = client
        self._owns_client = client is None

        # Pluggable resilience dependencies
        self.retry_policy = retry_policy or RetryPolicy(max_retries=settings.github.max_retries)
        self.circuit_breaker = circuit_breaker or CircuitBreaker(name="github_api")
        self.rate_limiter = rate_limiter or RateLimiter()

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazily initialize and return persistent httpx.AsyncClient with connection pooling."""
        if self._client is None or getattr(self._client, "is_closed", False) is True:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
            self._client = httpx.AsyncClient(timeout=self.timeout, limits=limits)
            self._owns_client = True
        return self._client

    @property
    def is_closed(self) -> bool:
        """Return True if the underlying AsyncClient is closed."""
        return self._client is not None and getattr(self._client, "is_closed", False) is True

    async def aclose(self) -> None:
        """Close underlying HTTP client session if owned by this instance."""
        if (
            self._owns_client
            and self._client is not None
            and not getattr(self._client, "is_closed", False)
        ):
            await self._client.aclose()

    async def __aenter__(self) -> "GitHubAPIClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def _get_headers(
        self,
        request_id: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if request_id:
            headers["X-Request-ID"] = request_id
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        return headers

    async def _execute_single_request(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        endpoint: str,
        request_id: str | None,
        etag: str | None,
    ) -> GitHubResponse:
        http_client = self.client
        start_time = time.perf_counter()

        try:
            response = await http_client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            raise NetworkError(f"HTTP request to GitHub API failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        res_headers = dict(response.headers)

        # Update rate limiter state from response headers
        remaining, reset_time, retry_after = self.rate_limiter.update_from_headers(res_headers)

        parts = endpoint.strip("/").split("/")
        owner = parts[1] if len(parts) >= 2 and parts[0] == "repos" else (parts[0] if parts else "unknown")
        repo = parts[2] if len(parts) >= 3 and parts[0] == "repos" else (parts[1] if len(parts) >= 2 else "unknown")

        logger.info(
            "GitHub API request execution",
            extra={
                "owner": owner,
                "repo": repo,
                "status": response.status_code,
                "latency_ms": latency_ms,
                "remaining_rate_limit": remaining,
                "request_id": request_id,
                "endpoint": endpoint,
            },
        )

        # Handle 304 Not Modified
        if response.status_code == 304:
            return GitHubResponse(
                data={},
                headers=res_headers,
                status_code=304,
                etag=etag or res_headers.get("ETag") or res_headers.get("etag"),
                last_modified=res_headers.get("Last-Modified") or res_headers.get("last-modified"),
                rate_limit_remaining=remaining,
                api_version=res_headers.get("X-GitHub-Api-Version"),
            )

        # Handle rate limits (403 / 429)
        if response.status_code in (403, 429) and (
            retry_after is not None or (remaining == 0 and reset_time is not None)
        ):
            await self.rate_limiter.wait_if_needed(retry_after=retry_after)

        # Domain error mappings
        if response.status_code == 404:
            raise RepositoryNotFound(f"Target GitHub resource not found: {endpoint}")
        if response.status_code == 401:
            raise Unauthorized("Unauthorized GitHub API request. Check GITHUB_TOKEN.")
        if response.status_code == 403 and remaining == 0:
            raise RateLimitExceeded(f"GitHub API rate limit exhausted for endpoint: {endpoint}")

        if response.status_code >= 400:
            response.raise_for_status()

        return GitHubResponse(
            data=response.json(),
            headers=res_headers,
            status_code=response.status_code,
            etag=res_headers.get("ETag") or res_headers.get("etag"),
            last_modified=res_headers.get("Last-Modified") or res_headers.get("last-modified"),
            rate_limit_remaining=remaining,
            api_version=res_headers.get("X-GitHub-Api-Version"),
        )

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
    ) -> GitHubResponse:
        """Fetch REST API resource protected by CircuitBreaker, RetryPolicy, and RateLimiter."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers(request_id=request_id, etag=etag, last_modified=last_modified)

        attempt = 0
        last_exc: Exception | None = None

        while attempt < self.retry_policy.max_retries:
            attempt += 1
            try:
                # Wrap request execution inside CircuitBreaker
                response = await self.circuit_breaker.call(
                    self._execute_single_request,
                    url=url,
                    headers=headers,
                    params=params,
                    endpoint=endpoint,
                    request_id=request_id,
                    etag=etag,
                )

                # Check if status warrants a retry via RetryPolicy
                if self.retry_policy.should_retry(response.status_code, attempt):
                    sleep_time = self.retry_policy.calculate_backoff(attempt)
                    logger.warning(
                        "Transient status received from GitHub API; backing off",
                        extra={"status_code": response.status_code, "attempt": attempt, "sleep_time": sleep_time},
                    )
                    await asyncio.sleep(sleep_time)
                    continue

                return response

            except (httpx.HTTPStatusError, NetworkError, GitHubError) as exc:
                last_exc = exc
                status_code = getattr(exc, "status_code", None)
                if isinstance(exc, httpx.HTTPStatusError):
                    status_code = exc.response.status_code

                if self.retry_policy.should_retry(status_code, attempt, exc=exc):
                    sleep_time = self.retry_policy.calculate_backoff(attempt)
                    logger.warning(
                        "Request attempt failed; backing off",
                        extra={"attempt": attempt, "error": str(exc), "sleep_time": sleep_time},
                    )
                    await asyncio.sleep(sleep_time)
                    continue

                raise

        if last_exc:
            raise last_exc
        raise NetworkError(f"Failed to fetch endpoint after {self.retry_policy.max_retries} attempts: {endpoint}")
