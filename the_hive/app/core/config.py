from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="null",
    )

    APP_NAME: str = "the_hive"
    
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/the_hive",
        description="PostgreSQL database connection URL",
    )
    
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT token signing and other crypto operations",
    )
    ADMIN_SESSION_SECRET: str = Field(
        default="admin-session-secret-change-in-production",
        description="Secret key for admin session management",
    )
    
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: str | list[str] = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Allowed CORS origins (comma-separated string or list)",
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:8000"]
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
