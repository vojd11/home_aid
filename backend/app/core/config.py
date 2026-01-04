from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600 # 1 year
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOG_LEVEL: str = "INFO"
    
    # Database
    POSTGRES_SERVER: str = "hate.local"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "home_aid_kit"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{info.data.get('POSTGRES_USER')}:"
            f"{info.data.get('POSTGRES_PASSWORD')}@"
            f"{info.data.get('POSTGRES_SERVER')}:"
            f"{info.data.get('POSTGRES_PORT')}/"
            f"{info.data.get('POSTGRES_DB')}"
        )

    # Redis
    REDIS_URL: str = "redis://hate.local:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://hate.local:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://hate.local:6379/2"
    
    # External APIs
    DRLZ_BASE_URL: str = "http://www.drlz.com.ua"
    TABLETKI_BASE_URL: str = "https://tabletki.ua"
    
    # Rate limiting
    REQUESTS_PER_SECOND: int = 1
    REQUESTS_PER_MINUTE_PER_HOUSEHOLD: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://hate.local:3000",
        "http://hate.local:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://hate.local:5173",
        "http://hate.local:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        raise ValueError(v)

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()
