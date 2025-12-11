"""
CRUD operations for database
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import models
import uuid
from datetime import datetime

# === Session Operations ===

def create_session(db: Session, user_id: Optional[str] = None) -> models.Session:
    """Create a new chat session"""
    session = models.Session(
        session_id=str(uuid.uuid4()),
        user_id=user_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: Session, session_id: str) -> Optional[models.Session]:
    """Get session by ID"""
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def delete_session(db: Session, session_id: str) -> bool:
    """Delete a session and all its messages"""
    session = get_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

# === Message Operations ===

def create_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    domain: Optional[str] = None,
    confidence: Optional[float] = None,
    sources: Optional[List[str]] = None,
    status: Optional[str] = None,
    retrieval_time: Optional[float] = None,
    generation_time: Optional[float] = None
) -> models.Message:
    """Create a new message with patent-ready fields"""
    
    # Build metadata
    metadata = {}
    if domain:
        metadata['domain'] = domain
    if confidence:
        metadata['confidence'] = confidence
    if sources:
        metadata['sources'] = sources
    if status:
        metadata['status'] = status
    
    # Create source UIDs (patent-ready)
    source_uids = None
    if sources:
        source_uids = [f"UID:doc:{hash(src)}" for src in sources]
    
    message = models.Message(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content,
        source_document_uids=source_uids,
        message_metadata=metadata,
        retrieval_time=retrieval_time,
        generation_time=generation_time
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_session_messages(
    db: Session,
    session_id: str,
    limit: int = 50
) -> List[models.Message]:
    """Get messages for a session, ordered by timestamp"""
    return db.query(models.Message)\
        .filter(models.Message.session_id == session_id)\
        .order_by(models.Message.timestamp.asc())\
        .limit(limit)\
        .all()

def get_message(db: Session, message_id: str) -> Optional[models.Message]:
    """Get a specific message by ID"""
    return db.query(models.Message).filter(models.Message.message_id == message_id).first()

# === User Operations ===

def create_user(
    db: Session,
    email: Optional[str] = None,
    name: str = "User",
    preferences: dict = None
) -> models.User:
    """Create a new user"""
    user = models.User(
        user_id=str(uuid.uuid4()),
        email=email,
        name=name,
        preferences=preferences or {}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

# === Audit Log Operations ===

def create_audit_log(
    db: Session,
    entity_uid: Optional[str],
    action_type: str,
    actor_id: Optional[str] = None,
    details: dict = None,
    trust_score: Optional[float] = None
) -> models.AuditLog:
    """Create an audit log entry (patent compliance)"""
    log = models.AuditLog(
        log_id=str(uuid.uuid4()),
        entity_uid=entity_uid,
        action_type=action_type,
        actor_id=actor_id,
        details=details or {},
        trust_score=trust_score
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_audit_logs(
    db: Session,
    entity_uid: Optional[str] = None,
    action_type: Optional[str] = None,
    limit: int = 100
) -> List[models.AuditLog]:
    """Get audit logs with optional filtering"""
    query = db.query(models.AuditLog)
    
    if entity_uid:
        query = query.filter(models.AuditLog.entity_uid == entity_uid)
    if action_type:
        query = query.filter(models.AuditLog.action_type == action_type)
    
    return query.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()

# === AI Agent Operations (for patent SubUID implementation) ===

def create_ai_agent(
    db: Session,
    agent_name: str,
    agent_type: str,
    parent_user_id: Optional[str] = None,
    permission_scopes: List[str] = None
) -> models.AIAgent:
    """Create an AI agent with SubUID (patent feature)"""
    agent = models.AIAgent(
        agent_id=str(uuid.uuid4()),
        agent_name=agent_name,
        agent_type=agent_type,
        parent_user_id=parent_user_id,
        permission_scopes=permission_scopes or []
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

def get_ai_agent(db: Session, agent_id: str) -> Optional[models.AIAgent]:
    """Get AI agent by ID"""
    return db.query(models.AIAgent).filter(models.AIAgent.agent_id == agent_id).first()

def revoke_ai_agent(db: Session, agent_id: str) -> bool:
    """Revoke an AI agent (patent security feature)"""
    agent = get_ai_agent(db, agent_id)
    if agent:
        agent.is_active = False
        agent.revoked_at = datetime.utcnow()
        db.commit()
        return True
    return False