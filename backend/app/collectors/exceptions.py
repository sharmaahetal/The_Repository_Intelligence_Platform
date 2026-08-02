class GitHubError(Exception):
    """Base domain exception for GitHub data collector subsystem."""

    pass


class RateLimitExceeded(GitHubError):
    """Raised when GitHub API rate limits are exhausted or Retry-After backoff is required."""

    pass


class RepositoryNotFound(GitHubError):
    """Raised when target GitHub repository is not found (HTTP 404)."""

    pass


class Unauthorized(GitHubError):
    """Raised when GitHub API authentication credentials are missing, invalid, or forbidden (HTTP 401/403)."""

    pass


class NetworkError(GitHubError):
    """Raised when an HTTP connection or request communication error occurs."""

    pass


class CircuitBreakerOpenError(GitHubError):
    """Raised when request is rejected because CircuitBreaker is in OPEN state."""

    pass


class ValidationError(GitHubError, ValueError):
    """Raised when raw GitHub payload validation fails."""

    pass
