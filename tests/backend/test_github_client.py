import httpx
import pytest
from app.collectors.github_client import GitHubAPIClient
from app.collectors.validator import RawPayloadValidator
from app.models.domain import RawRepositoryPayload


@pytest.mark.asyncio
async def test_github_client_reuse_and_headers():
    custom_httpx_client = httpx.AsyncClient()
    api_client = GitHubAPIClient(token="test_token", client=custom_httpx_client)

    # Verify connection pool client reuse
    assert api_client.client is custom_httpx_client

    headers = api_client._get_headers()
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"

    await api_client.aclose()
    await custom_httpx_client.aclose()


@pytest.mark.asyncio
async def test_github_client_context_manager():
    async with GitHubAPIClient(token="context_token") as client:
        assert client.client is not None
        assert not client.is_closed

    # Once exited, owned client should be closed
    assert client.is_closed


def test_raw_payload_validator():
    validator = RawPayloadValidator()
    raw_dict = {
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 100,
        "forks_count": 20,
    }

    validated = validator.validate_repository_payload(raw_dict)
    assert isinstance(validated, RawRepositoryPayload)
    assert validated.name == "vscode"
    assert validated.owner_login == "microsoft"
    assert validated.stargazers_count == 100

    with pytest.raises(ValueError):
        validator.validate_repository_payload("invalid string")  # type: ignore
