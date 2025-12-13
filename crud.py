"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models
import hashlib
import uuid

# === Session Operations ===

def create_session(db: Session, user_id: Optional[str] = None, title: Optional[str] = None) -> models.Session:
    """Create a new chat session"""
    session = models.Session(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: Session, session_id: str) -> Optional[models.Session]:
    """Get a session by ID"""
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def delete_session(db: Session, session_id: str) -> bool:
    """Delete a session and all its messages"""
    session = get_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def get_user_sessions(db: Session, user_id: Optional[str] = None, limit: int = 50) -> List[models.Session]:
    """Get all sessions for a user, ordered by most recent"""
    query = db.query(models.Session)
    
    if user_id:
        query = query.filter(models.Session.user_id == user_id)
    else:
        # Get anonymous sessions (no user_id)
        query = query.filter(models.Session.user_id == None)
    
    return query.order_by(models.Session.updated_at.desc()).limit(limit).all()

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
    """
    Create a new message in a session
    Automatically generates content hash
    """
    # Build metadata
    metadata = {}
    if domain:
        metadata['domain'] = domain
    if confidence is not None:
        metadata['confidence'] = confidence
    if sources:
        metadata['sources'] = sources
    if status:
        metadata['status'] = status
    
    # Generate content hash
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Generate source UIDs if sources provided
    source_uids = []
    if sources:
        source_uids = [f"UID:doc:{hash(src)}" for src in sources]
    
    message = models.Message(
        session_id=session_id,
        role=role,
        content=content,
        content_hash=content_hash,
        message_metadata=metadata,
        retrieval_time=retrieval_time,
        generation_time=generation_time,
        source_document_uids=source_uids
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update session timestamp
    session = get_session(db, session_id)
    if session:
        from datetime import datetime
        session.updated_at = datetime.utcnow()
        db.commit()
    
    return message

def get_session_messages(db: Session, session_id: str, limit: int = 100) -> List[models.Message]:
    """Get all messages for a session, ordered by timestamp"""
    return db.query(models.Message)\
        .filter(models.Message.session_id == session_id)\
        .order_by(models.Message.timestamp.asc())\
        .limit(limit)\
        .all()

def get_message(db: Session, message_id: str) -> Optional[models.Message]:
    """Get a single message by ID"""
    return db.query(models.Message).filter(models.Message.message_id == message_id).first()

# === User Operations ===

def create_user(
    db: Session,
    user_id: str = None,
    email: Optional[str] = None,
    name: Optional[str] = None,
    preferences: Optional[dict] = None
) -> models.User:
    """Create a new user"""
    user = models.User(
        user_id=user_id or str(uuid.uuid4()),
        email=email,
        name=name or 'User',
        preferences=preferences or {}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_preferences(db: Session, user_id: str, preferences: dict) -> Optional[models.User]:
    """Update user preferences"""
    user = get_user(db, user_id)
    if user:
        user.preferences = preferences
        db.commit()
        db.refresh(user)
    return user

def get_user_stats(db: Session, user_id: Optional[str] = None) -> dict:
    """Get user statistics - only counting sessions with messages"""
    
    # Get all sessions for the user
    sessions_query = db.query(models.Session)
    if user_id:
        sessions_query = sessions_query.filter(models.Session.user_id == user_id)
    
    all_sessions = sessions_query.all()
    
    # Count only sessions that have messages
    sessions_with_messages = 0
    for session in all_sessions:
        message_count = db.query(func.count(models.Message.message_id))\
            .filter(models.Message.session_id == session.session_id)\
            .scalar() or 0
        if message_count > 0:
            sessions_with_messages += 1
    
    total_sessions = sessions_with_messages
    
    # Count all messages for this user
    message_query = db.query(func.count(models.Message.message_id))
    if user_id:
        message_query = message_query.join(models.Session).filter(models.Session.user_id == user_id)
    total_messages = message_query.scalar() or 0
    
    # Count user queries (messages with role='user')
    query_query = db.query(func.count(models.Message.message_id))\
        .filter(models.Message.role == 'user')
    if user_id:
        query_query = query_query.join(models.Session).filter(models.Session.user_id == user_id)
    total_queries = query_query.scalar() or 0
    
    # Get domain distribution
    domain_query = db.query(models.Message.message_metadata).filter(models.Message.role == 'assistant')
    if user_id:
        domain_query = domain_query.join(models.Session).filter(models.Session.user_id == user_id)
    
    domains_used = {}
    for message in domain_query.all():
        metadata = message[0] if isinstance(message, tuple) else message.message_metadata
        if metadata and isinstance(metadata, dict) and 'domain' in metadata:
            domain = metadata['domain']
            domains_used[domain] = domains_used.get(domain, 0) + 1
    
    # Calculate average response time
    avg_time_query = db.query(func.avg(models.Message.generation_time))\
        .filter(models.Message.generation_time != None)
    if user_id:
        avg_time_query = avg_time_query.join(models.Session).filter(models.Session.user_id == user_id)
    avg_response_time = avg_time_query.scalar()
    
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "total_queries": total_queries,
        "domains_used": domains_used,
        "avg_response_time": float(avg_response_time) if avg_response_time else None
    }

# === Audit Log Operations ===

def create_audit_log(
    db: Session,
    entity_uid: Optional[str],
    action_type: str,
    actor_id: Optional[str] = None,
    details: Optional[dict] = None,
    trust_score: Optional[float] = None
) -> models.AuditLog:
    """Create an audit log entry"""
    log = models.AuditLog(
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
    actor_id: Optional[str] = None,
    limit: int = 100
) -> List[models.AuditLog]:
    """Get audit logs with optional filtering"""
    query = db.query(models.AuditLog)
    
    if entity_uid:
        query = query.filter(models.AuditLog.entity_uid == entity_uid)
    if actor_id:
        query = query.filter(models.AuditLog.actor_id == actor_id)
    
    return query.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()

# === AI Agent Operations ===

def create_ai_agent(
    db: Session,
    agent_name: str,
    agent_type: str,
    parent_user_id: Optional[str] = None,
    permission_scopes: Optional[List[str]] = None
) -> models.AIAgent:
    """Create an AI agent"""
    agent = models.AIAgent(
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
    """Get an AI agent by ID"""
    return db.query(models.AIAgent).filter(models.AIAgent.agent_id == agent_id).first()

def get_active_agents(db: Session, user_id: Optional[str] = None) -> List[models.AIAgent]:
    """Get all active AI agents, optionally filtered by user"""
    query = db.query(models.AIAgent).filter(models.AIAgent.is_active == True)
    if user_id:
        query = query.filter(models.AIAgent.parent_user_id == user_id)
    return query.all()