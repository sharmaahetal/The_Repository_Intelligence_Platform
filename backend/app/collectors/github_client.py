import asyncio
from typing import Any

import httpx
from app.config import github_settings
from app.logging import logger


class GitHubAPIClient:
    """Async HTTP client for interacting with GitHub REST and GraphQL APIs."""

    def __init__(self, token: str | None = None):
        self.token = token or github_settings.GITHUB_TOKEN
        self.base_url = github_settings.GITHUB_API_URL
        self.timeout = github_settings.REQUEST_TIMEOUT_SECONDS

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Fetch REST API resource with retries and rate limit handling."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(1, github_settings.MAX_RETRIES + 1):
                try:
                    response = await client.get(url, headers=headers, params=params)

                    # Handle GitHub Rate Limits
                    if (
                        response.status_code in (403, 429)
                        and "X-RateLimit-Remaining" in response.headers
                    ):
                        remaining = response.headers.get("X-RateLimit-Remaining", "0")
                        if remaining == "0":
                            reset_time = int(response.headers.get("X-RateLimit-Reset", "0"))
                            logger.warning(f"Rate limit reached. Reset: {reset_time}")
                            raise RuntimeError("GitHub API rate limit exceeded.")

                    response.raise_for_status()
                    return response.json()

                except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                    logger.warning(
                        f"[Attempt {attempt}/{github_settings.MAX_RETRIES}] Request failed: {exc}"
                    )
                    if attempt == github_settings.MAX_RETRIES:
                        raise
                    await asyncio.sleep(2**attempt)  # Exponential backoff

            raise RuntimeError(f"Failed to fetch endpoint: {endpoint}")
