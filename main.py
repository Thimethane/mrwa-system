"""
MRWA Main API Application
Complete FastAPI backend with graceful degradation
"""

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
import logging
import os

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="MRWA API",
    description="Marathon Research & Workflow Agent - Autonomous AI Research System",
    version="1.0.0",
)

# Load settings
try:
    from core.config import settings
    logger.info(f"✅ Settings loaded from .env")
    logger.info(f"   Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
    logger.info(f"   Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except Exception as e:
    logger.error(f"❌ Failed to load settings: {e}")
    # Create minimal settings
    class DummySettings:
        NODE_ENV = "development"
        cors_origins_list = ["*"]
        STORAGE_PATH = "./storage"
    settings = DummySettings()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'cors_origins_list', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import components with error handling
database_available = False
redis_available = False
orchestrator = None
storage_provider = None

# Try database
try:
    from core.database import init_db, close_db
    database_available = True
    logger.info("✅ Database module loaded")
except Exception as e:
    logger.warning(f"⚠️  Database module not available: {e}")
    async def init_db(): pass
    async def close_db(): pass

# Try Redis
try:
    from core.redis_client import redis_client
    redis_available = True
    logger.info("✅ Redis module loaded")
except Exception as e:
    logger.warning(f"⚠️  Redis module not available: {e}")
    class DummyRedis:
        async def connect(self): pass
        async def disconnect(self): pass
        async def set(self, *args, **kwargs): return True
        async def get(self, *args, **kwargs): return None
        async def exists(self, *args, **kwargs): return False
    redis_client = DummyRedis()

# Try Orchestrator
try:
    from core.orchestrator.engine import Orchestrator
    orchestrator = Orchestrator()
    logger.info("✅ Orchestrator initialized")
except Exception as e:
    logger.warning(f"⚠️  Orchestrator not available: {e}")

# Try Storage
try:
    from core.storage.provider import get_storage_provider
    storage_provider = get_storage_provider("local")
    logger.info("✅ Storage provider initialized")
except Exception as e:
    logger.warning(f"⚠️  Storage provider not available: {e}")

# Pydantic Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# In-memory user store for mock mode
mock_users = {}

# ============================================================================
# Startup & Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("="*60)
    logger.info("🚀 MRWA API Starting...")
    logger.info("="*60)
    
    # Try to initialize database
    if database_available:
        try:
            await init_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.warning(f"⚠️  Database initialization failed: {e}")
            logger.info("   Running in NO-DATABASE mode")
    else:
        logger.info("⚠️  Database: DISABLED (using mock data)")
    
    # Try to connect to Redis
    if redis_available:
        try:
            await redis_client.connect()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            logger.info("   Running in NO-REDIS mode")
    else:
        logger.info("⚠️  Redis: DISABLED (using in-memory)")
    
    logger.info("="*60)
    logger.info(f"📊 Status Summary:")
    logger.info(f"   Environment: {getattr(settings, 'NODE_ENV', 'development')}")
    logger.info(f"   Database: {'✅ Connected' if database_available else '❌ Disabled'}")
    logger.info(f"   Redis: {'✅ Connected' if redis_available else '❌ Disabled'}")
    logger.info(f"   Orchestrator: {'✅ Available' if orchestrator else '❌ Disabled'}")
    logger.info(f"   Storage: {'✅ Available' if storage_provider else '❌ Disabled'}")
    logger.info("="*60)
    logger.info("✅ MRWA API Ready!")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down MRWA API...")
    
    try:
        await redis_client.disconnect()
    except:
        pass
    
    try:
        await close_db()
    except:
        pass
    
    logger.info("✅ MRWA API shutdown complete")

# ============================================================================
# Basic Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MRWA",
        "version": "1.0.0",
        "status": "operational",
        "environment": getattr(settings, 'NODE_ENV', 'development'),
        "mode": "mock" if not database_available else "full",
        "components": {
            "database": database_available,
            "redis": redis_available,
            "orchestrator": orchestrator is not None,
            "storage": storage_provider is not None
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if database_available else "disabled",
        "redis": "connected" if redis_available else "disabled",
        "orchestrator": "available" if orchestrator else "disabled"
    }

# ============================================================================
# Mock Authentication Endpoints
# ============================================================================

@app.post("/api/v1/auth/signup")
async def signup(request_data: SignupRequest):
    """Create a new user account"""
    
    # Check if user already exists
    if request_data.email in mock_users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create mock user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": request_data.email,
        "name": request_data.name or "User",
        "created_at": datetime.utcnow().isoformat()
    }
    
    mock_users[request_data.email] = user
    
    logger.info(f"✅ User signup: {request_data.email}")
    
    return {
        "user": user,
        "access_token": f"mock_access_{user_id}",
        "refresh_token": f"mock_refresh_{user_id}",
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/login")
async def login(request_data: LoginRequest):
    """Authenticate user"""
    
    # Get or create user
    user = mock_users.get(request_data.email)
    
    if not user:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": request_data.email,
            "name": "User",
            "created_at": datetime.utcnow().isoformat()
        }
        mock_users[request_data.email] = user
    
    logger.info(f"✅ User login: {request_data.email}")
    
    return {
        "user": user,
        "access_token": f"mock_access_{user['id']}",
        "refresh_token": f"mock_refresh_{user['id']}",
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}

@app.post("/api/v1/auth/refresh")
async def refresh_token():
    """Refresh access token"""
    user_id = str(uuid.uuid4())
    return {
        "access_token": f"mock_access_{user_id}",
        "refresh_token": f"mock_refresh_{user_id}",
        "token_type": "bearer"
    }

@app.get("/api/v1/user/profile")
async def get_profile():
    """Get current user profile"""
    return {
        "id": str(uuid.uuid4()),
        "email": "user@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat(),
        "statistics": {
            "total_executions": 0,
            "successful_executions": 0,
            "total_artifacts": 0
        }
    }

# ============================================================================
# File Upload & Execution Endpoints
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
                file.content_type or "application/octet-stream"
            )
        else:
            file_url = f"/storage/uploads/{uuid.uuid4()}{Path(file.filename).suffix}"
        
        logger.info(f"✅ File uploaded: {file.filename}")
        
        return {
            "success": True,
            "filename": file.filename,
            "file_url": file_url,
            "content_type": file.content_type,
            "size_bytes": len(file_data)
        }
        
    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/v1/executions")
async def create_execution(payload: dict):
    """Create and start a new execution"""
    
    execution_id = str(uuid.uuid4())
    
    logger.info(f"✅ Creating execution: {payload.get('input_type')}")
    
    # Generate plan
    if orchestrator:
        try:
            plan_steps = await orchestrator.generate_plan(
                payload.get('input_type', 'pdf'),
                payload.get('input_value', 'test')
            )
            plan = [step.to_dict() for step in plan_steps]
        except Exception as e:
            logger.warning(f"Plan generation failed: {e}, using default")
            plan = [
                {"id": 1, "name": "Process input", "status": "pending"},
                {"id": 2, "name": "Analyze content", "status": "pending"},
                {"id": 3, "name": "Generate output", "status": "pending"}
            ]
    else:
        plan = [
            {"id": 1, "name": "Process input", "status": "pending"},
            {"id": 2, "name": "Analyze content", "status": "pending"},
            {"id": 3, "name": "Generate output", "status": "pending"}
        ]
    
    return {
        "execution_id": execution_id,
        "status": "planned",
        "plan": plan,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/executions")
async def list_executions(page: int = 1, limit: int = 20):
    """List user's executions"""
    return {
        "executions": [],
        "total": 0,
        "page": page,
        "pages": 0
    }

@app.get("/api/v1/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get detailed execution information"""
    return {
        "id": execution_id,
        "user_id": str(uuid.uuid4()),
        "input_type": "pdf",
        "input_value": "test.pdf",
        "status": "completed",
        "plan": [],
        "current_step": 0,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
