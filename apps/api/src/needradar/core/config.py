from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://needradar:needradar_local@127.0.0.1:5432/needradar"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str = DEFAULT_DATABASE_URL
    cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [
            AnyHttpUrl("http://localhost:3000"),
            AnyHttpUrl("http://127.0.0.1:3000"),
        ]
    )
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"
    sse_heartbeat_seconds: int = 15
    alembic_config_path: Path = Path("apps/api/alembic.ini")

    @field_validator("database_url")
    @classmethod
    def require_psycopg_driver(cls, value: str) -> str:
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use the postgresql+psycopg driver")
        return value

    @field_validator("api_host")
    @classmethod
    def require_local_default_host(cls, value: str) -> str:
        if value == "0.0.0.0":
            raise ValueError("API_HOST must not use the public 0.0.0.0 bind")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            raise ValueError("CORS_ORIGINS must be a JSON array of local origins")
        if isinstance(value, list) and "*" in value:
            raise ValueError("Wildcard CORS origins are forbidden")
        return value

    @field_validator("cors_origins")
    @classmethod
    def require_local_http_origins(cls, value: list[AnyHttpUrl]) -> list[AnyHttpUrl]:
        for origin in value:
            if (
                origin.scheme != "http"
                or origin.host not in {"localhost", "127.0.0.1"}
                or origin.username is not None
                or origin.password is not None
                or origin.query is not None
                or origin.fragment is not None
                or origin.path not in {None, "", "/"}
            ):
                raise ValueError(
                    "CORS_ORIGINS entries must be local http origins without credentials, "
                    "path, query, or fragment"
                )
        return value


def load_settings() -> Settings:
    env_file = os.environ.get("NEEDRADAR_ENV_FILE", ".env")
    return Settings(_env_file=env_file if Path(env_file).exists() else None)
