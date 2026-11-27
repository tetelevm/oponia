from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr

    admin_username: str = "admin"
    admin_password: SecretStr = SecretStr("")
    admin_secret_key: SecretStr = SecretStr("")

    @model_validator(mode="after")
    def validate_admin(self) -> "Settings":
        if self.admin_password.get_secret_value():
            if not self.admin_username.strip():
                raise ValueError("ADMIN_USERNAME must not be blank")
            if not self.admin_secret_key.get_secret_value():
                raise ValueError("ADMIN_SECRET_KEY is required with ADMIN_PASSWORD")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
