from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Intranet Escolar"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/intranet_escolar"
    frontend_origins: str = (
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:8001,http://127.0.0.1:8001"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
