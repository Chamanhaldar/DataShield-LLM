from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Sentinel LLM Guard"
    api_prefix: str = "/v1"
    token_vault_key: str
    database_url: str = "sqlite+aiosqlite:///./tokens.db"
    openai_api_key: str | None = None
    allowed_policies: list[str] = ["default", "block-on-leak"]
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
