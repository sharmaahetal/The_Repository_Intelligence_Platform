from typing import Any

from app.collectors.github_client import GitHubAPIClient, GitHubResponse
from app.logging import logger


class RepositoryCollector:
    """Collector for fetching raw GitHub repository metadata without validation or orchestration coupling."""

    def __init__(self, client: GitHubAPIClient | None = None):
        self.client = client or GitHubAPIClient()

    async def fetch_repository(
        self, owner: str, repo: str, request_id: str | None = None
    ) -> GitHubResponse:
        """Fetch raw primary repository response from /repos/{owner}/{repo}."""
        logger.info(
            "Collecting raw metadata for repository",
            extra={"owner": owner, "repo": repo, "request_id": request_id},
        )
        endpoint = f"repos/{owner}/{repo}"
        response = await self.client.get(endpoint, request_id=request_id)

        if not isinstance(response.data, dict):
            raise ValueError(f"Unexpected response format from GitHub API for {owner}/{repo}")

        return response
