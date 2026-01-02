import os
from typing import Optional, List, Literal
from pydantic import Field, AnyUrl, PostgresDsn
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MRWA"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(default="development", env="NODE_ENV")
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ALGORITHM: Literal["HS256", "RS256"] = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    REDIS_URL: Optional[AnyUrl] = None
    REDIS_MAX_CONNECTIONS: int = 50

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = 8192

    STORAGE_PROVIDER: Literal["local", "s3", "supabase"] = "local"
    STORAGE_PATH: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "storage"))

    SUPABASE_URL: Optional[AnyUrl] = None
    SUPABASE_KEY: Optional[str] = None

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_EXECUTION_TIME_SECONDS: int = 3600
    MAX_RETRIES_PER_STEP: int = 3
    SENTRY_DSN: Optional[AnyUrl] = None

    # ───────────────────────────
    # Pydantic Settings Config
    # ───────────────────────────
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    # ───────────────────────────
    # Helpers
    # ───────────────────────────
    @property
    def abs_storage_path(self) -> str:
        """
        Returns an absolute, normalized path for storage,
        always safe to write in Codespaces / local dev.
        """
        return os.path.abspath(self.STORAGE_PATH)

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return str(self.DATABASE_URL)
        else:
            return f"sqlite+aiosqlite:///{os.path.join(os.getcwd(), 'dev.db')}"


# Singleton
settings = Settings()
