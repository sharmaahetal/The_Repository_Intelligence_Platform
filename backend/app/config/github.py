from pydantic_settings import BaseSettings, SettingsConfigDict


class GitHubSettings(BaseSettings):
    GITHUB_TOKEN: str | None = None
    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_GRAPHQL_URL: str = "https://api.github.com/graphql"
    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


github_settings = GitHubSettings()
