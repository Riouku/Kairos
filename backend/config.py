from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    app_name: str = "Intranet Escolar"
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/intranet_escolar",
        validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_URL"),
    )
    frontend_origins: str = (
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:8001,http://127.0.0.1:8001"
    )

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
