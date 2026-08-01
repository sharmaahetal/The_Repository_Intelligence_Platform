from typing import Any

from backend.app.collectors.github_client import GitHubAPIClient, GitHubResponse
from backend.app.collectors.validator import RawPayloadValidator
from backend.app.logging import logger
from backend.app.models.raw_payload import RawRepositoryPayload


class RepositoryCollector:
    """Orchestration collector fetching GitHub repository payloads and passing them to validator.

    Strictly handles orchestration only: Repository -> GitHubClient -> Validator.
    Never stores data or builds snapshots.
    """

    def __init__(
        self,
        client: GitHubAPIClient | None = None,
        validator: RawPayloadValidator | None = None,
    ):
        self.client = client or GitHubAPIClient()
        self.validator = validator or RawPayloadValidator()

    async def fetch_repository(
        self,
        owner: str,
        repo: str,
        request_id: str | None = None,
        etag: str | None = None,
    ) -> GitHubResponse:
        """Fetch raw primary repository response from /repos/{owner}/{repo}."""
        logger.info(
            "Collecting raw metadata for repository",
            extra={"owner": owner, "repo": repo, "request_id": request_id},
        )
        endpoint = f"repos/{owner}/{repo}"
        response = await self.client.get(endpoint, request_id=request_id, etag=etag)

        if not isinstance(response.data, dict) and response.status_code != 304:
            raise ValueError(f"Unexpected response format from GitHub API for {owner}/{repo}")

        return response

    async def collect_repository(
        self,
        owner: str,
        repo: str,
        request_id: str | None = None,
        etag: str | None = None,
    ) -> RawRepositoryPayload:
        """Orchestrate collection pipeline: fetch payload via GitHubClient -> validate via Validator."""
        response = await self.fetch_repository(owner=owner, repo=repo, request_id=request_id, etag=etag)

        raw_dict: dict[str, Any] = response.data if isinstance(response.data, dict) else {}
        return self.validator.validate_repository_payload(
            raw_data=raw_dict,
            headers=response.headers,
            request_id=request_id,
        )
