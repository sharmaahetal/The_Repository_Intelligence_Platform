import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.app.collectors import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    GitHubAPIClient,
    GitHubResponse,
    NetworkError,
    RateLimitExceeded,
    RateLimiter,
    RepositoryNotFound,
    RetryPolicy,
    Unauthorized,
    ValidationError,
)


@pytest.mark.asyncio
async def test_retry_policy_unit_behavior():
    policy = RetryPolicy(max_retries=3, base_delay=1.0)
    assert policy.should_retry(500, attempt=1)
    assert policy.should_retry(503, attempt=2)
    assert not policy.should_retry(500, attempt=3)
    assert not policy.should_retry(404, attempt=1)

    delay = policy.calculate_backoff(attempt=1)
    assert 1.0 <= delay <= 3.0


@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions():
    breaker = CircuitBreaker(name="test_breaker", failure_threshold=2, recovery_timeout=0.1)
    assert breaker.state == CircuitState.CLOSED

    # Record 1 failure
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED

    # Record 2nd failure -> Trips to OPEN
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN

    # In OPEN state, call() immediately raises CircuitBreakerOpenError
    async def sample_target():
        return "success"

    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call(sample_target)

    # Wait recovery_timeout -> transitions to HALF_OPEN
    await asyncio.sleep(0.15)
    result = await breaker.call(sample_target)
    assert result == "success"
    assert breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_rate_limiter_unit_behavior():
    limiter = RateLimiter(buffer_seconds=1)
    headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700000000"}
    limiter.update_from_headers(headers)
    assert limiter.remaining == 0
    assert limiter.reset_timestamp == 1700000000

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with patch("time.time", return_value=1699999990):
            slept = await limiter.wait_if_needed()
            assert slept == 11.0
            mock_sleep.assert_called_once_with(11.0)


@pytest.mark.asyncio
async def test_github_client_domain_exception_mappings():
    mock_httpx = AsyncMock()
    mock_httpx.is_closed = False
    req = httpx.Request("GET", "https://api.github.com/repos/nonexistent/repo")

    # 404 Not Found -> RepositoryNotFound
    mock_httpx.get.return_value = httpx.Response(status_code=404, request=req)
    async with GitHubAPIClient(client=mock_httpx) as client:
        with pytest.raises(RepositoryNotFound):
            await client.get("repos/nonexistent/repo")

    # 401 Unauthorized -> Unauthorized
    mock_httpx.get.return_value = httpx.Response(status_code=401, request=req)
    async with GitHubAPIClient(client=mock_httpx) as client:
        with pytest.raises(Unauthorized):
            await client.get("repos/secret/repo")


@pytest.mark.asyncio
async def test_conditional_request_metadata():
    resp = GitHubResponse(
        data={},
        headers={"ETag": 'W/"123"', "Last-Modified": "Wed, 21 Oct 2015 07:28:00 GMT"},
        status_code=304,
        etag='W/"123"',
        last_modified="Wed, 21 Oct 2015 07:28:00 GMT",
    )
    assert resp.is_not_modified is True
    assert resp.etag == 'W/"123"'
    assert resp.last_modified == "Wed, 21 Oct 2015 07:28:00 GMT"
    assert resp.snapshot_time != ""
