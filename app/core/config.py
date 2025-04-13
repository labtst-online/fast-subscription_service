import os
from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_core import MultiHostUrl
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, extra='ignore')

    APP_ENV: str = "development"

    # Postgres Database Config
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    PAYMENT_SERVICE_URL: str = "http://payment_service:8004"

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_PAYMENT_EVENTS_TOPIC: str = "payment_events"
    KAFKA_CONSUMER_GROUP_ID: str = "subscription_service_group"

    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            # If the URI is already provided as a string, use it directly
            return v
        # Otherwise, build it from components
        values = info.data
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
