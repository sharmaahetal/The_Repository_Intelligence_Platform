from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.app.collectors.github_client import GitHubAPIClient
from backend.app.collectors.retry import (
    calculate_exponential_backoff,
    calculate_rate_limit_sleep,
    is_retryable_status,
    parse_rate_limit_headers,
)
from backend.app.collectors.validator import RawPayloadValidator
from backend.app.models.domain import RawRepositoryPayload


@pytest.mark.asyncio
async def test_github_client_reuse_and_headers():
    custom_httpx_client = httpx.AsyncClient()
    api_client = GitHubAPIClient(token="test_token", client=custom_httpx_client)

    # Verify connection pool client reuse
    assert api_client.client is custom_httpx_client

    headers = api_client._get_headers(request_id="req-101", etag='W/"etag123"')
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert headers["X-Request-ID"] == "req-101"
    assert headers["If-None-Match"] == 'W/"etag123"'

    await api_client.aclose()
    await custom_httpx_client.aclose()


@pytest.mark.asyncio
async def test_github_client_context_manager():
    async with GitHubAPIClient(token="context_token") as client:
        assert client.client is not None
        assert not client.is_closed

    # Once exited, owned client should be closed
    assert client.is_closed


@pytest.mark.asyncio
async def test_github_client_etag_304_handling():
    mock_httpx = AsyncMock()
    mock_httpx.is_closed = False
    req = httpx.Request("GET", "https://api.github.com/repos/octocat/Hello-World")
    mock_httpx.get.return_value = httpx.Response(
        status_code=304,
        headers={"ETag": 'W/"etag123"', "X-RateLimit-Remaining": "4900"},
        request=req,
    )

    async with GitHubAPIClient(token="token", client=mock_httpx) as client:
        res = await client.get("repos/octocat/Hello-World", etag='W/"etag123"')

        assert res.status_code == 304
        assert res.data == {}
        assert res.etag == 'W/"etag123"'
        assert res.rate_limit_remaining == 4900


@pytest.mark.asyncio
async def test_github_client_retry_on_500_transient_error():
    mock_httpx = AsyncMock()
    mock_httpx.is_closed = False

    req = httpx.Request("GET", "https://api.github.com/repos/octocat/Hello-World")
    fail_response = httpx.Response(status_code=502, json={"message": "Bad Gateway"}, request=req)
    success_response = httpx.Response(
        status_code=200,
        headers={"ETag": 'W/"abc"', "X-RateLimit-Remaining": "4999"},
        json={"id": 1, "name": "Hello-World"},
        request=req,
    )

    mock_httpx.get.side_effect = [fail_response, success_response]

    with (
        patch(
            "backend.app.collectors.github_client.calculate_exponential_backoff", return_value=0.001
        ),
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        async with GitHubAPIClient(token="token", client=mock_httpx) as client:
            res = await client.get("repos/octocat/Hello-World")
            assert res.status_code == 200
            assert isinstance(res.data, dict)
            assert res.data["name"] == "Hello-World"
            assert mock_sleep.called


def test_retry_helpers():
    assert is_retryable_status(500)
    assert is_retryable_status(502)
    assert is_retryable_status(503)
    assert is_retryable_status(504)
    assert is_retryable_status(429)
    assert not is_retryable_status(404)
    assert not is_retryable_status(401)

    backoff = calculate_exponential_backoff(attempt=1, base_delay=2.0)
    assert 2.0 <= backoff <= 4.0

    rem, reset, retry_after = parse_rate_limit_headers(
        {
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": "1700000000",
            "Retry-After": "5",
        }
    )
    assert rem == 10
    assert reset == 1700000000
    assert retry_after == 5

    sleep_time = calculate_rate_limit_sleep(reset_timestamp=1700000000)
    assert sleep_time >= 0.0


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
