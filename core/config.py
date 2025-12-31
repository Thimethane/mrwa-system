"""
Configuration management for MRWA
Loads environment variables and provides application configuration
"""

from typing import Optional, List, Literal
from pydantic import Field, AnyUrl, PostgresDsn
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All values are read from `.env` and the OS environment.
    Unknown variables are allowed to support multi-service deployments.
    """

    # ───────────────────────────
    # Application
    # ───────────────────────────
    APP_NAME: str = "MRWA"
    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        env="NODE_ENV",
        description="Application runtime environment",
    )

    DEBUG: bool = False

    # ───────────────────────────
    # Security / Auth
    # ───────────────────────────
    JWT_SECRET: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT signing (min 32 chars)",
    )

    JWT_ALGORITHM: Literal["HS256", "RS256"] = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ───────────────────────────
    # Database
    # ───────────────────────────
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection string",
    )

    DATABASE_POOL_SIZE: int = Field(default=10, ge=1)
    DATABASE_MAX_OVERFLOW: int = Field(default=20, ge=0)

    # ───────────────────────────
    # Redis / Caching
    # ───────────────────────────
    REDIS_URL: Optional[AnyUrl] = None
    REDIS_MAX_CONNECTIONS: int = Field(default=50, ge=1)

    # ───────────────────────────
    # AI Service (Gemini)
    # ───────────────────────────
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = Field(default=8192, ge=256)

    # ───────────────────────────
    # Storage
    # ───────────────────────────
    STORAGE_PROVIDER: Literal["local", "s3", "supabase"] = "local"
    STORAGE_PATH: str = "./storage"

    SUPABASE_URL: Optional[AnyUrl] = None
    SUPABASE_KEY: Optional[str] = None

    # ───────────────────────────
    # CORS
    # ───────────────────────────
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # ───────────────────────────
    # Rate Limiting
    # ───────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)

    # ───────────────────────────
    # Execution / Workers
    # ───────────────────────────
    MAX_EXECUTION_TIME_SECONDS: int = Field(default=3600, ge=60)
    MAX_RETRIES_PER_STEP: int = Field(default=3, ge=0)

    # ───────────────────────────
    # Monitoring / Logging
    # ───────────────────────────
    SENTRY_DSN: Optional[AnyUrl] = None
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ───────────────────────────
    # Pydantic Settings Config
    # ───────────────────────────
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # Allow unrelated env vars (Docker, CI, Node, etc.)
    )


# Global settings instance (singleton)
settings = Settings()
