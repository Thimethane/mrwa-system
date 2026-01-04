"""
Database connection and session management with graceful degradation
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# -------------------------------
# Import settings from .env
# -------------------------------
from core.config import settings

# Use database URL from settings only
DATABASE_URL = settings.database_url

# -------------------------------
# SQLAlchemy Base
# -------------------------------
Base = declarative_base()

# -------------------------------
# Engine and session placeholders
# -------------------------------
engine = None
AsyncSessionLocal = None

# -------------------------------
# Initialize engine and session
# -------------------------------
try:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE or 10,
        max_overflow=settings.DATABASE_MAX_OVERFLOW or 20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    logger.info("✅ Database engine created successfully")
except Exception as e:
    engine = None
    AsyncSessionLocal = None
    logger.error(f"❌ Failed to create database engine: {e}")
    logger.info("Database functionality is disabled until proper configuration is provided.")

# -------------------------------
# Dependency to get DB session
# -------------------------------
async def get_db() -> AsyncSession:
    """Provide an async database session"""
    if not AsyncSessionLocal:
        raise RuntimeError("Database session unavailable. Check your configuration.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# -------------------------------
# Initialize database tables
# -------------------------------
async def init_db():
    """Initialize database tables"""
    if not engine:
        logger.warning("Database engine unavailable. Skipping table initialization.")
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

# -------------------------------
# Close database connections
# -------------------------------
async def close_db():
    """Dispose database engine"""
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed")
