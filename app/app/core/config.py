from os import environ
import secrets
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Sendcloud RSS Feeder"
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24 * 8
    )  # 60 minutes * 24 hours * 8 days = 8 days
    SECRET_KEY = secrets.token_urlsafe(32)

    # Database
    POSTGRES_SERVER: str = environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = environ.get("POSTGRES_DB", "postgres")

    # Celery
    CELERY_BROKER_URL: str = environ.get("CELERY_BROKER_URL")
    FEED_REFRESH_INTERVAL: int = 5

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
