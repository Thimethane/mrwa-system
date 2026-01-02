"""
Database connection and session management
"""

import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

logger = logging.getLogger(__name__)

# ───────────────────────────────
# Helper: build DATABASE_URL dynamically
# ───────────────────────────────
def build_database_url() -> str:
    """
    Construct async Postgres URL from environment / settings
    """
    user = os.getenv("POSTGRES_USER", "mrwa")
    password = os.getenv("POSTGRES_PASSWORD", "mrwa_password")
    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    dbname = os.getenv("DATABASE_NAME", "mrwa")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


# Create async engine
engine = create_async_engine(
    build_database_url(),
    pool_size=int(settings.DATABASE_POOL_SIZE),
    max_overflow=int(settings.DATABASE_MAX_OVERFLOW),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI: yield an async DB session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db():
    """Dispose engine connections"""
    await engine.dispose()
    logger.info("Database connections closed")
