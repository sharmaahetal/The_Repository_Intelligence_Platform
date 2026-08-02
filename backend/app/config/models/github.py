from pydantic import Field

from backend.app.config.base import BaseAppSettings


class GitHubConfig(BaseAppSettings):
    token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    api_url: str = Field(default="https://api.github.com", validation_alias="GITHUB_API_URL")
    graphql_url: str = Field(default="https://api.github.com/graphql", validation_alias="GITHUB_GRAPHQL_URL")
    request_timeout_seconds: int = Field(default=30, validation_alias="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, validation_alias="MAX_RETRIES")
