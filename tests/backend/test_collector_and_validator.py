from unittest.mock import AsyncMock

import httpx
import pytest

from backend.app.collectors.github_client import GitHubAPIClient, GitHubResponse
from backend.app.collectors.repository_collector import RepositoryCollector
from backend.app.collectors.validator import RawPayloadValidator
from backend.app.models.raw_payload import RawRepositoryPayload


def test_validator_valid_payload():
    validator = RawPayloadValidator()
    raw_dict = {
        "id": 999,
        "name": "fastapi",
        "owner": {"login": "tiangolo"},
        "stargazers_count": 60000,
        "created_at": "2018-12-05T00:00:00Z",
    }
    headers = {"ETag": 'W/"abc12345"', "X-Request-ID": "req-777"}

    payload = validator.validate_repository_payload(raw_dict, headers=headers, request_id="req-777")
    assert isinstance(payload, RawRepositoryPayload)
    assert payload.name == "fastapi"
    assert payload.owner_login == "tiangolo"
    assert payload.etag == 'W/"abc12345"'
    assert payload.request_id == "req-777"


def test_validator_reject_missing_name():
    validator = RawPayloadValidator()
    raw_dict = {"owner": {"login": "tiangolo"}}

    with pytest.raises(ValueError, match="missing required non-empty string field 'name'"):
        validator.validate_repository_payload(raw_dict)


def test_validator_reject_missing_owner():
    validator = RawPayloadValidator()
    raw_dict = {"name": "fastapi", "owner": {}}

    with pytest.raises(ValueError, match="missing non-empty 'login' handle"):
        validator.validate_repository_payload(raw_dict)


def test_validator_reject_invalid_id():
    validator = RawPayloadValidator()
    raw_dict = {"id": -5, "name": "fastapi", "owner": {"login": "tiangolo"}}

    with pytest.raises(ValueError, match="must be a positive integer"):
        validator.validate_repository_payload(raw_dict)


def test_validator_reject_invalid_timestamp():
    validator = RawPayloadValidator()
    raw_dict = {
        "name": "fastapi",
        "owner": {"login": "tiangolo"},
        "created_at": "not-a-valid-timestamp",
    }

    with pytest.raises(ValueError, match="Invalid timestamp format"):
        validator.validate_repository_payload(raw_dict)


@pytest.mark.asyncio
async def test_repository_collector_orchestration():
    mock_client = AsyncMock(spec=GitHubAPIClient)
    mock_client.get.return_value = GitHubResponse(
        data={
            "id": 100,
            "name": "react",
            "owner": {"login": "facebook"},
            "stargazers_count": 210000,
        },
        headers={"ETag": 'W/"12345"', "X-Request-ID": "req-999"},
        status_code=200,
        etag='W/"12345"',
        rate_limit_remaining=4999,
        api_version="2022-11-28",
    )

    collector = RepositoryCollector(client=mock_client)
    payload = await collector.collect_repository("facebook", "react", request_id="req-999")

    assert isinstance(payload, RawRepositoryPayload)
    assert payload.name == "react"
    assert payload.owner_login == "facebook"
    assert payload.stargazers_count == 210000
    mock_client.get.assert_called_once_with("repos/facebook/react", request_id="req-999", etag=None)
