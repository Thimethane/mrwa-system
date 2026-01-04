"""
Redis client for caching and session management with graceful degradation
"""

import logging
from typing import Optional, Any
import json

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("redis package not installed")
    REDIS_AVAILABLE = False

# Try to load settings
try:
    from core.config import settings
    REDIS_URL = settings.redis_url
except Exception as e:
    logger.warning(f"Could not load settings: {e}")
    REDIS_URL = "redis://localhost:6379"


class RedisClient:
    """Async Redis client wrapper with graceful degradation"""
    
    def __init__(self):
        self.redis: Optional[Any] = None
        self.available = False
        self._in_memory_cache = {}
    
    async def connect(self):
        """Connect to Redis with fallback to in-memory"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  Redis not available, using in-memory cache")
            self.available = False
            return
        
        try:
            self.redis = await redis.from_url(
                REDIS_URL,
                max_connections=50,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            await self.redis.ping()
            self.available = True
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            logger.info("Using in-memory cache instead")
            self.redis = None
            self.available = False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            try:
                await self.redis.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis: {e}")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value with optional expiration"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if self.redis and self.available:
            try:
                return await self.redis.set(key, value, ex=expire)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}, using in-memory")
        
        # Fallback to in-memory
        self._in_memory_cache[key] = value
        return True
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if self.redis and self.available:
            try:
                return await self.redis.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}, using in-memory")
        
        # Fallback to in-memory
        return self._in_memory_cache.get(key)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value by key"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def delete(self, key: str) -> bool:
        """Delete key"""
        if self.redis and self.available:
            try:
                return await self.redis.delete(key) > 0
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        
        # Fallback to in-memory
        if key in self._in_memory_cache:
            del self._in_memory_cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.redis and self.available:
            try:
                return await self.redis.exists(key) > 0
            except Exception as e:
                logger.warning(f"Redis exists failed: {e}")
        
        # Fallback to in-memory
        return key in self._in_memory_cache
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if self.redis and self.available:
            try:
                return await self.redis.incrby(key, amount)
            except Exception as e:
                logger.warning(f"Redis increment failed: {e}")
        
        # Fallback to in-memory
        current = int(self._in_memory_cache.get(key, 0))
        new_value = current + amount
        self._in_memory_cache[key] = str(new_value)
        return new_value


# Global Redis client instance
redis_client = RedisClient()
