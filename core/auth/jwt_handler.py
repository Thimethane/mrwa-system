# ============================================================================
# core/auth/jwt_handler.py - JWT Token Management
# ============================================================================

import jwt
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """JWT token creation and validation"""
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create JWT access token"""
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token() -> str:
        """Create random refresh token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    @staticmethod
    def get_token_user_id(token: str) -> Optional[str]:
        """Extract user ID from token"""
        payload = JWTHandler.decode_token(token)
        if payload:
            return payload.get("sub")
        return None
