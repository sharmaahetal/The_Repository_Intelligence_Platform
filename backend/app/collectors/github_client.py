import asyncio
from typing import Any

import httpx
from app.config import github_settings
from app.logging import logger


class GitHubAPIClient:
    """Async HTTP client for interacting with GitHub REST and GraphQL APIs using a reusable connection pool."""

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

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Fetch REST API resource with retries, connection pooling, and rate limit handling."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        http_client = self.client
        if http_client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True
            http_client = self._client

        for attempt in range(1, github_settings.MAX_RETRIES + 1):
            try:
                response = await http_client.get(url, headers=headers, params=params)

                # Handle GitHub Rate Limits
                if (
                    response.status_code in (403, 429)
                    and "X-RateLimit-Remaining" in response.headers
                ):
                    remaining = response.headers.get("X-RateLimit-Remaining", "0")
                    if remaining == "0":
                        reset_time = int(response.headers.get("X-RateLimit-Reset", "0"))
                        logger.warning(
                            "GitHub API rate limit exceeded",
                            extra={"reset_time": reset_time, "endpoint": endpoint},
                        )
                        raise RuntimeError("GitHub API rate limit exceeded.")

                response.raise_for_status()
                return response.json()

            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                logger.warning(
                    "Request attempt failed",
                    extra={
                        "attempt": attempt,
                        "max_retries": github_settings.MAX_RETRIES,
                        "endpoint": endpoint,
                        "error": str(exc),
                    },
                )
                if attempt == github_settings.MAX_RETRIES:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

        raise RuntimeError(f"Failed to fetch endpoint: {endpoint}")
