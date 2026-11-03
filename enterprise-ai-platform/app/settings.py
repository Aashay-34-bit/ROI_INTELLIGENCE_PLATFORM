from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    api_key: str = "demo-key"
    database_url: str = "sqlite:///./platform.db"
    default_strategy: str = "cost_quality"
    model_provider: str = "mock"
    mock_failure_rate: float = 0.0
    mock_min_latency_ms: int = 50
    mock_max_latency_ms: int = 500
    jev_base_url: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"


@lru_cache
def get_settings() -> Settings:
    return Settings()
