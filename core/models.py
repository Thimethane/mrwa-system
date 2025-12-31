# ============================================================================
# core/models.py - Database Models
# ============================================================================

from sqlalchemy import Column, String, Boolean, Integer, Text, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from core.database import Base
import uuid


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP(timezone=True))
    email_verified = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSONB, default={})  # Renamed for Python, DB column remains 'metadata'


class Session(Base):
    """User session model for device tracking"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    device_info = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_used_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    revoked = Column(Boolean, default=False)


class Execution(Base):
    """Workflow execution model"""
    __tablename__ = "executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    input_type = Column(String(50), nullable=False)
    input_value = Column(Text, nullable=False)
    input_file_url = Column(Text)
    status = Column(String(50), nullable=False, default='planned', index=True)
    plan = Column(JSONB)
    current_step = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    metadata_ = Column("metadata", JSONB, default={})  # Renamed for Python
    error_message = Column(Text)


class ExecutionLog(Base):
    """Execution log entries"""
    __tablename__ = "execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('executions.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB)  # Renamed for Python
    step_id = Column(Integer)


class Artifact(Base):
    """Generated artifacts"""
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('executions.id', ondelete='CASCADE'), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    name = Column(String(255))
    data = Column(JSONB)
    file_url = Column(Text)
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
