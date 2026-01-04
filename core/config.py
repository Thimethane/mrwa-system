"""
Configuration management for MRWA
Loads environment variables and provides application configuration
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "MRWA"
    APP_VERSION: str = "1.0.0"
    NODE_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = "INFO"
    
    # Security
    JWT_SECRET: str = Field(default="dev-secret-change-in-production-min-32-chars")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database - All optional
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "mrwa"
    POSTGRES_PASSWORD: str = "mrwa_password"
    DATABASE_NAME: str = "mrwa"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis - All optional
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_MAX_CONNECTIONS: int = 50
    
    # AI Service - Optional
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = 8192
    
    # Storage - All optional
    STORAGE_PROVIDER: str = "local"
    STORAGE_PATH: str = "./storage"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Execution
    MAX_EXECUTION_TIME_SECONDS: int = 3600
    MAX_RETRIES_PER_STEP: int = 3
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Build database URL if not provided"""
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            return self.DATABASE_URL
        
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Build Redis URL if not provided"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string"""
        if isinstance(self.CORS_ORIGINS, str):
            origins = self.CORS_ORIGINS.strip('[]"')
            return [o.strip().strip('"').strip("'") for o in origins.split(',') if o.strip()]
        return self.CORS_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields


# Global settings instance with error handling
settings = None

try:
    settings = Settings()
    print("✅ Settings loaded successfully from .env")
except Exception as e:
    print(f"❌ Critical Error: Invalid or missing environment variables in .env")
    print(str(e))
    print("\n⚠️  Using default settings for development mode")
    
    # Create minimal working settings
    class DefaultSettings:
        APP_NAME = "MRWA"
        APP_VERSION = "1.0.0"
        NODE_ENV = "development"
        DEBUG = False
        LOG_LEVEL = "INFO"
        JWT_SECRET = "dev-secret-change-in-production-min-32-chars"
        JWT_ALGORITHM = "HS256"
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
        JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
        STORAGE_PATH = "./storage"
        STORAGE_PROVIDER = "local"
        CORS_ORIGINS = "http://localhost:3000"
        RATE_LIMIT_ENABLED = True
        RATE_LIMIT_PER_MINUTE = 60
        MAX_EXECUTION_TIME_SECONDS = 3600
        MAX_RETRIES_PER_STEP = 3
        GEMINI_API_KEY = None
        GEMINI_MODEL = "gemini-pro"
        SUPABASE_URL = None
        SUPABASE_KEY = None
        DATABASE_HOST = "localhost"
        DATABASE_PORT = 5432
        REDIS_HOST = "localhost"
        REDIS_PORT = 6379
        
        @property
        def database_url(self):
            return "postgresql+asyncpg://mrwa:mrwa_password@localhost:5432/mrwa"
        
        @property
        def redis_url(self):
            return "redis://localhost:6379"
        
        @property
        def cors_origins_list(self):
            return ["*"]
    
    settings = DefaultSettings()
