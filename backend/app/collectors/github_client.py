import asyncio
import random
from dataclasses import dataclass
from typing import Any

import httpx

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
    """Async HTTP client for interacting with GitHub APIs with connection pooling, retries, jitter, and Retry-After support."""

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
        """Lazily initialize and return the reusable httpx.AsyncClient instance."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True
        return self._client

    @property
    def is_closed(self) -> bool:
        """Return True if the underlying AsyncClient is closed."""
        return self._client is not None and self._client.is_closed

    async def aclose(self) -> None:
        """Close underlying HTTP client session if owned by this instance."""
        if self._owns_client and self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> "GitHubAPIClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def _get_headers(self, request_id: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if request_id:
            headers["X-Request-ID"] = request_id
        return headers

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> GitHubResponse:
        """Fetch REST API resource with connection pooling, retries, jitter, and Retry-After handling."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers(request_id=request_id)

        http_client = self.client
        if http_client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True
            http_client = self._client

        max_retries = github_settings.MAX_RETRIES

        for attempt in range(1, max_retries + 1):
            try:
                response = await http_client.get(url, headers=headers, params=params)

                # Handle 429 Rate Limits / Retry-After
                if response.status_code in (403, 429):
                    retry_after_str = response.headers.get("Retry-After")
                    if retry_after_str and retry_after_str.isdigit():
                        sleep_seconds = int(retry_after_str)
                        logger.warning(
                            "Rate limit exceeded with Retry-After header",
                            extra={
                                "endpoint": endpoint,
                                "sleep_seconds": sleep_seconds,
                                "request_id": request_id,
                            },
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(sleep_seconds)
                            continue

                    remaining = response.headers.get("X-RateLimit-Remaining", "0")
                    if remaining == "0":
                        reset_time = int(response.headers.get("X-RateLimit-Reset", "0"))
                        logger.warning(
                            "GitHub API rate limit exceeded",
                            extra={
                                "reset_time": reset_time,
                                "endpoint": endpoint,
                                "request_id": request_id,
                            },
                        )
                        raise RuntimeError("GitHub API rate limit exceeded.")

                # Retry on transient server error status codes (500, 502, 503, 504)
                if response.status_code in (500, 502, 503, 504):
                    logger.warning(
                        "Transient server error from GitHub API",
                        extra={
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "endpoint": endpoint,
                            "request_id": request_id,
                        },
                    )
                    if attempt < max_retries:
                        backoff = (2**attempt) + random.uniform(0.1, 1.0)
                        await asyncio.sleep(backoff)
                        continue

                response.raise_for_status()

                # Extract response metadata
                res_headers = dict(response.headers)
                rate_remaining = (
                    int(res_headers["X-RateLimit-Remaining"])
                    if "X-RateLimit-Remaining" in res_headers
                    and res_headers["X-RateLimit-Remaining"].isdigit()
                    else None
                )

                return GitHubResponse(
                    data=response.json(),
                    headers=res_headers,
                    status_code=response.status_code,
                    etag=res_headers.get("ETag") or res_headers.get("etag"),
                    rate_limit_remaining=rate_remaining,
                    api_version=res_headers.get("X-GitHub-Api-Version"),
                )

            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                logger.warning(
                    "Request attempt failed",
                    extra={
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "endpoint": endpoint,
                        "request_id": request_id,
                        "error": str(exc),
                    },
                )
                if attempt == max_retries:
                    raise
                backoff = (2**attempt) + random.uniform(0.1, 1.0)
                await asyncio.sleep(backoff)

        raise RuntimeError(f"Failed to fetch endpoint: {endpoint}")
