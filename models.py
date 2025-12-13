"""
Database models with patent-ready architecture
Patent-ready architecture with UID placeholders
"""
from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import hashlib

Base = declarative_base()

class User(Base):
    """User accounts """
    __tablename__ = "user_profiles"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persistent_uid = Column(String, unique=True, nullable=True)  # PATENT: Cryptographic UID placeholder
    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)
    preferences = Column(JSON, default=dict)  # User preferences (diet, health goals, etc.)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    """Chat sessions with conversation history"""
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_uid = Column(String, unique=True, nullable=True)  # PATENT: Placeholder for cryptographic session UID
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=True)  # NULL = anonymous session
    title = Column(String, nullable=True)  # Chat title (auto-generated from first message)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """Individual messages in conversations"""
    __tablename__ = "messages"
    
    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_uid = Column(String, unique=True, nullable=True)  # PATENT: Placeholder for cryptographic message UID
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=True)  # SHA-256 hash of content (PATENT: tamper detection)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # RAG metadata
    message_metadata = Column(JSON, default=dict)  # Store domain, confidence, sources, status
    retrieval_time = Column(Float, nullable=True)  # Seconds
    generation_time = Column(Float, nullable=True)  # Seconds
    
    # PATENT: Source document tracking
    source_document_uids = Column(JSON, default=list)  # List of UIDs for documents used
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate content hash on creation
        if self.content and not self.content_hash:
            self.content_hash = self._generate_content_hash(self.content)
    
    @staticmethod
    def _generate_content_hash(content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

class AuditLog(Base):
    """Audit trail for all system actions (PATENT: provenance tracking)"""
    __tablename__ = "audit_logs"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_uid = Column(String, nullable=True)  # PATENT: UID of entity being acted upon
    action_type = Column(String, nullable=False)  # 'create', 'read', 'update', 'delete', 'query', etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor_id = Column(String, nullable=True)  # User or AI agent that performed action
    details = Column(JSON, default=dict)  # Additional context
    trust_score = Column(Float, nullable=True)  # PATENT: Trust/reputation score
    verified = Column(Boolean, default=False)  # PATENT: Cryptographic verification status

class AIAgent(Base):
    """AI Agent tracking (PATENT: SubUID system for agent hierarchy)"""
    __tablename__ = "ai_agents"
    
    agent_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_uid = Column(String, unique=True, nullable=True)  # PATENT: Cryptographic SubUID
    agent_name = Column(String, nullable=False)  # e.g., "Holistic Health Agent", "Finance Agent"
    agent_type = Column(String, nullable=False)  # e.g., "rag", "reasoning", "tool_use"
    parent_user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=True)
    permission_scopes = Column(JSON, default=list)  # What the agent can access
    is_active = Column(Boolean, default=True)
    behavior_signature = Column(String, nullable=True)  # PATENT: Hash of agent's behavior/prompts
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)