"""
MRWA Main API Application
Complete FastAPI backend with authentication, execution management, and real-time updates
"""

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import uuid
import logging
import os
import json

# ============================================================================
# ENVIRONMENT (PARSED DIRECTLY FROM .env)
# ============================================================================

NODE_ENV = os.getenv("NODE_ENV", "development")
APP_NAME = os.getenv("APP_NAME", "MRWA")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15))

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ============================================================================
# Logging
# ============================================================================
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Initialization (UNCHANGED LOGIC)
# ============================================================================
app = FastAPI(
    title=APP_NAME,
    description="Marathon Research & Workflow Agent - Autonomous AI Research System",
    version=APP_VERSION,
    debug=DEBUG,
)

# ============================================================================
# CORS (PARSED FROM .env ONLY)
# ============================================================================
try:
    CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", "[]"))
except json.JSONDecodeError:
    CORS_ORIGINS = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Security
# ============================================================================
security = HTTPBearer()

# ============================================================================
# Imports AFTER ENV is loaded (UNCHANGED)
# ============================================================================
from core.config import settings
from core.database import get_db, init_db, close_db, AsyncSessionLocal
from core.redis_client import redis_client
from core.models import User, Session, Execution, ExecutionLog, Artifact
from core.auth.password import PasswordManager
from core.auth.jwt_handler import JWTHandler
from core.orchestrator.engine import Orchestrator
from core.validation.validator import Validator
from core.correction.corrector import Corrector
from core.storage.provider import get_storage_provider
from ingestion.document_parser.pdf_parser import PDFParser
from ingestion.code_analyzer.analyzer import CodeAnalyzer
from ingestion.web_scraper.scraper import WebScraper
from ingestion.media_processor.youtube_processor import YouTubeProcessor

# ============================================================================
# Component Initialization (LOGIC UNCHANGED)
# ============================================================================
orchestrator = Orchestrator() if GEMINI_API_KEY else None
validator = Validator()
corrector = Corrector()
password_manager = PasswordManager()
jwt_handler = JWTHandler()
storage_provider = get_storage_provider(STORAGE_PROVIDER)

pdf_parser = PDFParser()
code_analyzer = CodeAnalyzer()
web_scraper = WebScraper()
youtube_processor = YouTubeProcessor()

# ============================================================================
# Startup & Shutdown (UNCHANGED)
# ============================================================================
@app.on_event("startup")
async def startup_event():
    logger.info("Starting MRWA API...")
    await init_db()
    await redis_client.connect()
    logger.info(f"MRWA started in {NODE_ENV}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MRWA API...")
    await redis_client.disconnect()
    await close_db()

# ============================================================================
# Basic Endpoints (UNCHANGED)
# ============================================================================
@app.get("/")
async def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "environment": NODE_ENV,
        "demo_mode": orchestrator is None
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# EVERYTHING BELOW THIS POINT IS 100% UNCHANGED
# (Auth, uploads, executions, mocks, etc.)
# ============================================================================
# ============================================================================
# Pydantic Models
# ============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============================================================================
# Mock Authentication Endpoints (for testing without database)
# ============================================================================

@app.post("/api/v1/auth/signup", response_model=Dict)
async def signup(request_data: SignupRequest):
    """Create a new user account (mock version)"""

    user_id = str(uuid.uuid4())
    access_token = f"mock_access_token_{user_id}"
    refresh_token = f"mock_refresh_token_{user_id}"

    logger.info(f"Mock signup: {request_data.email}")

    return {
        "user": {
            "id": user_id,
            "email": request_data.email,
            "name": request_data.name,
            "created_at": datetime.utcnow().isoformat()
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/api/v1/auth/login")
async def login(request_data: LoginRequest):
    """Authenticate user (mock version)"""

    user_id = str(uuid.uuid4())
    access_token = f"mock_access_token_{user_id}"
    refresh_token = f"mock_refresh_token_{user_id}"

    logger.info(f"Mock login: {request_data.email}")

    return {
        "user": {
            "id": user_id,
            "email": request_data.email,
            "name": "Mock User",
            "created_at": datetime.utcnow().isoformat()
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/api/v1/auth/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}


@app.get("/api/v1/user/profile")
async def get_profile():
    """Get current user profile (mock version)"""

    return {
        "id": str(uuid.uuid4()),
        "email": "user@example.com",
        "name": "Mock User",
        "created_at": datetime.utcnow().isoformat(),
        "statistics": {
            "total_executions": 0,
            "successful_executions": 0,
            "total_artifacts": 0
        }
    }


# ============================================================================
# File Upload Endpoint
# ============================================================================

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for processing"""

    try:
        file_data = await file.read()

        if storage_provider:
            file_url = await storage_provider.save_file(
                file_data,
                file.filename,
                file.content_type
            )
        else:
            file_url = f"/storage/uploads/{uuid.uuid4()}{Path(file.filename).suffix}"

        logger.info(f"File uploaded: {file.filename}")

        return {
            "success": True,
            "filename": file.filename,
            "file_url": file_url,
            "content_type": file.content_type,
            "size_bytes": len(file_data)
        }

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


# ============================================================================
# Execution Endpoints (Mock)
# ============================================================================

@app.post("/api/v1/executions")
async def create_execution(payload: dict):
    """Create and start a new execution (mock version)"""

    execution_id = str(uuid.uuid4())

    logger.info(f"Creating execution: {payload.get('input_type')}")

    plan = [
        {"id": 1, "name": "Extract and analyze input", "status": "pending"},
        {"id": 2, "name": "Process content", "status": "pending"},
        {"id": 3, "name": "Generate insights", "status": "pending"},
        {"id": 4, "name": "Create final artifact", "status": "pending"}
    ]

    return {
        "execution_id": execution_id,
        "status": "planned",
        "plan": plan,
        "created_at": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/executions")
async def list_executions(page: int = 1, limit: int = 20):
    """List user's executions (mock version)"""

    return {
        "executions": [],
        "total": 0,
        "page": page,
        "pages": 0
    }


@app.get("/api/v1/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get detailed execution information (mock version)"""

    return {
        "id": execution_id,
        "user_id": str(uuid.uuid4()),
        "input_type": "pdf",
        "input_value": "test.pdf",
        "status": "completed",
        "plan": {},
        "current_step": 4,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }
