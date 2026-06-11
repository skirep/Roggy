"""ROGI application configuration via environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_path: str = "rogi.db"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Email accounts (comma-separated JSON configs)
    gmail_accounts: str = ""     # JSON list of {email, app_password}
    outlook_accounts: str = ""   # JSON list of {email, password, host, port}
    imap_accounts: str = ""      # JSON list of {label, host, port, username, password, ssl}

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Open WebUI
    open_webui_url: str = "http://localhost:3000"

    # n8n
    n8n_url: str = "http://localhost:5678"
    n8n_webhook_url: str = ""

    # Digest schedule (cron-style, used by background job)
    digest_cron: str = "0 7 * * *"  # 07:00 every day

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
