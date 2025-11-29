"""Application configuration."""

import os
from datetime import timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # JWT Configuration
    SECRET_KEY: str = "snake-playground-pro-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./snake_playground.db"
    DATABASE_ECHO: bool = False  # Set to True for SQL logging
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Environment
    ENVIRONMENT: str = "development"  # development, testing, production

    # CORS Configuration
    CODESPACE_NAME: str | None = None
    GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN: str = "app.github.dev"

    @property
    def ACCESS_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        """Get token expiration as timedelta."""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Get CORS origins including Codespaces URLs if applicable."""
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]

        if self.CODESPACE_NAME:
            codespaces_urls = [
                f"https://{self.CODESPACE_NAME}-5173.{self.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
                f"https://{self.CODESPACE_NAME}-3000.{self.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
                f"https://{self.CODESPACE_NAME}-8080.{self.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
            ]
            origins.extend(codespaces_urls)

        return origins

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == "testing"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

# Backward compatibility exports
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ACCESS_TOKEN_EXPIRE_DELTA = settings.ACCESS_TOKEN_EXPIRE_DELTA
CORS_ORIGINS = settings.CORS_ORIGINS
CODESPACE_NAME = settings.CODESPACE_NAME
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = settings.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN
