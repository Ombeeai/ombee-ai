"""
Database models with patent-ready architecture
Includes placeholder fields for future UID implementation
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import hashlib

Base = declarative_base()

class User(Base):
    """User table - ready for patent authentication"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persistent_uid = Column(String, nullable=True)  # PATENT: Will store persistent UID
    email = Column(String, unique=True, nullable=True)
    name = Column(String)
    preferences = Column(JSON, default=dict)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    """Chat session table"""
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_uid = Column(String, nullable=True)  # PATENT: Will store session UID
    user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """Message table with patent-ready provenance fields"""
    __tablename__ = "messages"
    
    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_uid = Column(String, nullable=True)  # PATENT: Will store cryptographic UID
    session_id = Column(String, ForeignKey('sessions.session_id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    content_hash = Column(String)  # SHA-256 hash of content (patent provenance)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # PATENT: Source tracking fields
    source_document_uids = Column(JSON, nullable=True)  # Array of source UIDs
    
    # Message metadata for patent features (renamed to avoid SQLAlchemy conflict)
    message_metadata = Column(JSON, default=dict)  # Stores domain, confidence, sources, etc.
    
    # Performance metrics (patent: reasoning authentication)
    retrieval_time = Column(Float, nullable=True)  # seconds
    generation_time = Column(Float, nullable=True)  # seconds
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate content hash on creation
        if self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

class AuditLog(Base):
    """Audit log for patent compliance - tracks all AI interactions"""
    __tablename__ = "audit_logs"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_uid = Column(String, nullable=True)  # PATENT: UID of the entity being logged
    action_type = Column(String)  # 'query', 'response', 'retrieval', etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor_id = Column(String, nullable=True)  # user_id or agent_id
    
    # PATENT: Detailed logging
    details = Column(JSON, default=dict)  # Stores full context of action
    
    # PATENT: Trust and verification
    trust_score = Column(Float, nullable=True)
    verified = Column(Boolean, default=False)

class AIAgent(Base):
    """AI Agent table - for patent SubUID implementation"""
    __tablename__ = "ai_agents"
    
    agent_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_uid = Column(String, nullable=True)  # PATENT: Agent SubUID
    agent_name = Column(String)
    agent_type = Column(String)  # 'rag', 'router', 'retriever', etc.
    parent_user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    
    # PATENT: Permission and scope
    permission_scopes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    
    # PATENT: Behavioral attestation
    behavior_signature = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)