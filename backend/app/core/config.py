"""
INTENTA — Application Configuration
Environment-based settings via Pydantic Settings v2.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "INTENTA"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # LLM / Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_timeout: int = 180
    ollama_max_retries: int = 3
    ollama_retry_delay: float = 2.0

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "intenta"

    # CORS
    allowed_origins: List[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
