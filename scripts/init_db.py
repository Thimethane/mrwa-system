# ============================================================================
# scripts/init_db.py - Database Initialization Script
# ============================================================================

"""
Initialize database with migrations
Run: python scripts/init_db.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alembic.config import Config
from alembic import command
from core.database import engine, Base
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database with schema"""
    try:
        # Create all tables (for development)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def run_migrations():
    """Run Alembic migrations"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("🔧 Initializing database...")
    
    # Run migrations
    run_migrations()
    
    # Initialize database
    asyncio.run(init_database())
    
    print("✅ Database ready!")
