from typing import Optional, Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_prefix=""
    )

    SQL_HOST: str
    SQL_PORT: str
    SQL_USERNAME: Optional[str] = None
    SQL_PASSWORD: Optional[str] = None
    SQL_DATABASE: str

    SQL_TABLE_DATA: Optional[str] = "data"
    SQL_TABLE_ENTRY: Optional[str] = "entry"
    SQL_TABLE_CATEGORY: Optional[str] = "category"


def env_settings(other_env: str = None) -> Settings:
    if other_env:
        return Settings(_env_file=other_env)
    return Settings()


envs = env_settings()
