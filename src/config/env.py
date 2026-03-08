from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql://whatflix:whatflix@db:5432/whatflix"
    jwt_secret: str = "replace-me"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    tmdb_api_key: str | None = None
    tmdb_bearer: str | None = None
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_timeout_seconds: float = 5.0


settings = Settings()
