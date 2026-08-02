import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.collectors.retry import (
    calculate_exponential_backoff,
    calculate_rate_limit_sleep,
    is_retryable_status,
    parse_rate_limit_headers,
)
from backend.app.config import github_settings
from backend.app.logging import logger


@dataclass
class GitHubResponse:
    """Wrapper holding raw response payload along with HTTP response metadata."""

    data: dict[str, Any] | list[dict[str, Any]]
    headers: dict[str, str]
    status_code: int
    etag: str | None = None
    rate_limit_remaining: int | None = None
    api_version: str | None = None


class GitHubAPIClient:
    """Async HTTP client for GitHub API with connection pooling, retry backoff with jitter, ETag 304, and rate limits."""

    def __init__(
        self,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self.token = token or github_settings.GITHUB_TOKEN
        self.base_url = github_settings.GITHUB_API_URL
        self.timeout = github_settings.REQUEST_TIMEOUT_SECONDS
        self._client = client
        self._owns_client = client is None

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
        self, request_id: str | None = None, etag: str | None = None
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
        return headers

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
        etag: str | None = None,
    ) -> GitHubResponse:
        """Fetch REST API resource with connection pooling, retries, jitter, ETag 304, and rate-limit wait."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers(request_id=request_id, etag=etag)
        http_client = self.client

        # Parse owner/repo from endpoint if available for structured logging
        parts = endpoint.strip("/").split("/")
        owner = (
            parts[1]
            if len(parts) >= 2 and parts[0] == "repos"
            else (parts[0] if parts else "unknown")
        )
        repo = (
            parts[2]
            if len(parts) >= 3 and parts[0] == "repos"
            else (parts[1] if len(parts) >= 2 else "unknown")
        )

        max_retries = github_settings.MAX_RETRIES

        for attempt in range(1, max_retries + 1):
            start_time = time.perf_counter()
            try:
                response = await http_client.get(url, headers=headers, params=params)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                res_headers = dict(response.headers)
                remaining, reset_time, retry_after = parse_rate_limit_headers(res_headers)

                # Structured log for every request
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
                        rate_limit_remaining=remaining,
                        api_version=res_headers.get("X-GitHub-Api-Version"),
                    )

                # Handle 429 Rate Limit / Retry-After
                if response.status_code in (403, 429):
                    if retry_after is not None:
                        logger.warning(
                            "Rate limit exceeded; sleeping Retry-After interval",
                            extra={
                                "endpoint": endpoint,
                                "sleep_seconds": retry_after,
                                "request_id": request_id,
                                "attempt": attempt,
                            },
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(retry_after)
                            continue

                    if remaining == 0 and reset_time is not None:
                        sleep_seconds = calculate_rate_limit_sleep(reset_time)
                        logger.warning(
                            "GitHub rate limit depleted; sleeping until reset",
                            extra={
                                "reset_time": reset_time,
                                "sleep_seconds": sleep_seconds,
                                "endpoint": endpoint,
                                "request_id": request_id,
                                "attempt": attempt,
                            },
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(sleep_seconds)
                            continue

                # Retry on transient server errors (500, 502, 503, 504)
                if is_retryable_status(response.status_code):
                    logger.warning(
                        "Transient HTTP error from GitHub API; backing off",
                        extra={
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "endpoint": endpoint,
                            "request_id": request_id,
                        },
                    )
                    if attempt < max_retries:
                        sleep_time = calculate_exponential_backoff(attempt)
                        await asyncio.sleep(sleep_time)
                        continue

                response.raise_for_status()

                return GitHubResponse(
                    data=response.json(),
                    headers=res_headers,
                    status_code=response.status_code,
                    etag=res_headers.get("ETag") or res_headers.get("etag"),
                    rate_limit_remaining=remaining,
                    api_version=res_headers.get("X-GitHub-Api-Version"),
                )

            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.warning(
                    "Request attempt failed",
                    extra={
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "endpoint": endpoint,
                        "request_id": request_id,
                        "latency_ms": latency_ms,
                        "error": str(exc),
                    },
                )
                if attempt == max_retries:
                    raise
                sleep_time = calculate_exponential_backoff(attempt)
                await asyncio.sleep(sleep_time)

        raise RuntimeError(f"Failed to fetch endpoint after {max_retries} attempts: {endpoint}")
