# ============================================================================
# scripts/cleanup_storage.py - Storage Cleanup Script
# ============================================================================

"""
Clean up old storage files
Run: python scripts/cleanup_storage.py
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import AsyncSessionLocal
from core.models import Execution, Artifact
from sqlalchemy import select, and_
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cleanup_old_files(days_old: int = 90):
    """Delete files from executions older than specified days"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    async with AsyncSessionLocal() as db:
        # Find old executions
        result = await db.execute(
            select(Execution).where(
                and_(
                    Execution.completed_at < cutoff_date,
                    Execution.status.in_(['completed', 'failed'])
                )
            )
        )
        old_executions = result.scalars().all()
        
        logger.info(f"Found {len(old_executions)} old executions to clean up")
        
        storage_path = Path("./storage")
        deleted_count = 0
        
        for execution in old_executions:
            # Delete associated file
            if execution.input_file_url:
                file_path_parts = execution.input_file_url.strip('/').split('/')
                if len(file_path_parts) >= 3:
                    file_path = storage_path / file_path_parts[1] / file_path_parts[2]
                    if file_path.exists():
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted: {file_path}")
            
            # Delete execution record
            await db.delete(execution)
        
        await db.commit()
        
        logger.info(f"Cleanup complete: {deleted_count} files deleted")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up old storage files')
    parser.add_argument('--days', type=int, default=90,
                       help='Delete files older than this many days (default: 90)')
    
    args = parser.parse_args()
    
    asyncio.run(cleanup_old_files(args.days))
