from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://hiremind:password@localhost:5432/hiremind"
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI
    openai_api_key: str = ""

    # Judge0
    # Free local Judge0: docker compose -f docker-compose.judge0.yml up -d
    judge0_api_url: str = "http://127.0.0.1:2358"
    judge0_api_key: str = ""

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "hiremind-media"
    aws_region: str = "ap-south-1"

    # App
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://127.0.0.1:8000"
    environment: str = "development"
    proctoring_enabled: bool = True
    ai_evaluation_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
