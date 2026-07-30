from typing import Any

from app.collectors.github_client import GitHubAPIClient
from app.logging import logger


class RepositoryCollector:
    """Collector for fetching raw GitHub repository metadata."""

    def __init__(self, client: GitHubAPIClient | None = None):
        self.client = client or GitHubAPIClient()

    async def fetch_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch primary repository metadata from /repos/{owner}/{repo}."""
        logger.info(f"Collecting raw metadata for repository: {owner}/{repo}")
        endpoint = f"repos/{owner}/{repo}"
        data = await self.client.get(endpoint)

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected response format from GitHub API for {owner}/{repo}")

        return data
