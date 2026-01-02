"""
Redis connection management
"""

import os
import logging
import redis
from core.config import settings

logger = logging.getLogger(__name__)

def build_redis_url() -> str:
    """
    Construct Redis URL from env / settings
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    return f"redis://{host}:{port}"


try:
    redis_client = redis.from_url(
        str(settings.REDIS_URL) if settings.REDIS_URL else build_redis_url(),
        decode_responses=True,
        max_connections=int(settings.REDIS_MAX_CONNECTIONS)
    )
    redis_client.ping()  # test connection
    logger.info("Redis client initialized successfully")

except Exception as e:
    redis_client = None
    logger.error(f"Failed to initialize Redis client: {e}")
