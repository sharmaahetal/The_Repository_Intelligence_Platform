from typing import Any

from app.collectors.github_client import GitHubAPIClient
from app.collectors.validator import RawPayloadValidator
from app.logging import logger
from app.models.domain import RawRepositoryPayload


class RepositoryCollector:
    """Collector for fetching and validating raw GitHub repository metadata."""

    def __init__(
        self,
        client: GitHubAPIClient | None = None,
        validator: RawPayloadValidator | None = None,
    ):
        self.client = client or GitHubAPIClient()
        self.validator = validator or RawPayloadValidator()

    async def fetch_repository(self, owner: str, repo: str) -> RawRepositoryPayload:
        """Fetch primary repository metadata from /repos/{owner}/{repo} and return validated model."""
        logger.info(
            "Collecting raw metadata for repository",
            extra={"owner": owner, "repo": repo},
        )
        endpoint = f"repos/{owner}/{repo}"
        data = await self.client.get(endpoint)

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected response format from GitHub API for {owner}/{repo}")

        return self.validator.validate_repository_payload(data)
