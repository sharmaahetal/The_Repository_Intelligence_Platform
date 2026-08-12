from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class GitHubConfig(BaseModel):
    """GitHub API client authentication and API versioning configuration."""

    model_config = ConfigDict(populate_by_name=True)

    token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GITHUB_TOKEN", "GITHUB__TOKEN"),
    )
    api_version: str = Field(
        default="2022-11-28",
        validation_alias=AliasChoices("GITHUB_API_VERSION", "GITHUB__API_VERSION"),
    )
    api_url: str = Field(
        default="https://api.github.com",
        validation_alias=AliasChoices("GITHUB_API_URL", "GITHUB__API_URL"),
    )
    graphql_url: str = Field(
        default="https://api.github.com/graphql",
        validation_alias=AliasChoices("GITHUB_GRAPHQL_URL", "GITHUB__GRAPHQL_URL"),
    )
    request_timeout_seconds: int = Field(
        default=30,
        validation_alias=AliasChoices("REQUEST_TIMEOUT_SECONDS", "GITHUB__REQUEST_TIMEOUT_SECONDS"),
    )
    max_retries: int = Field(
        default=3,
        validation_alias=AliasChoices("MAX_RETRIES", "GITHUB__MAX_RETRIES"),
    )
