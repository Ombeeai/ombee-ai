"""
Ombee AI FastAPI Backend
Production-ready with patent architecture foundations
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import json

# Import database models and operations
from database import SessionLocal, engine, get_db
import models
import crud

# Import existing RAG components
from src.router import detect_domain
from src.retriever import retrieve_context
from src.llm import generate_response
from src.demo_responses import get_demo_response, get_coming_soon_message
from src.monitoring import get_monitor

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Ombee AI API",
    description="Multi-domain RAG chatbot with patent-ready architecture",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

monitor = get_monitor()

# === Request/Response Models ===

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    response: str
    domain: str
    confidence: float
    sources: List[str]
    status: str
    timestamp: str
    content_hash: Optional[str] = None
    source_document_uids: Optional[List[str]] = None

class SessionCreate(BaseModel):
    user_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: str

class MessageHistory(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: str
    domain: Optional[str] = None
    sources: Optional[List[str]] = None

# === API Endpoints ===

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ombee AI",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/sessions/create", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db = Depends(get_db)
):
    """Create a new chat session"""
    try:
        session = crud.create_session(db, session_data.user_id)
        
        return SessionResponse(
            session_id=session.session_id,
            created_at=session.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db = Depends(get_db)
):
    """
    Main chat endpoint - processes user query through RAG pipeline
    """
    try:
        # Get or create session
        if request.session_id:
            session = crud.get_session(db, request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = crud.create_session(db, request.user_id)
        
        # Store user message
        user_message = crud.create_message(
            db=db,
            session_id=session.session_id,
            role="user",
            content=request.message
        )
        
        # Get conversation history for context (last 5 messages)
        history = crud.get_session_messages(db, session.session_id, limit=10)
        conversation_context = ""
        if len(history) > 1:  # More than just the current message
            # Format last few exchanges for context
            recent_messages = history[-6:-1] if len(history) > 6 else history[:-1]
            conversation_context = "\n".join([
                f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content[:200]}" 
                for msg in recent_messages
            ])
        
        # Domain routing
        domain, confidence = detect_domain(request.message)
        
        # Initialize response variables
        response_text = ""
        sources = []
        status = ""
        context = ""
        retrieval_time = None
        generation_time = None
        cumulative_tokens = None
        cumulative_cost = None
        
        # Check for demo response
        demo_response = get_demo_response(request.message, domain)
        
        if demo_response:
            response_text = demo_response['response']
            sources = demo_response['sources']
            status = demo_response['status']
            
        elif domain == 'holistic':
            # Real RAG pipeline
            try:
                # Retrieve context
                context, sources, retrieval_time = retrieve_context(request.message)
                
                # Add conversation history to context if available
                if conversation_context:
                    context = f"Previous conversation:\n{conversation_context}\n\n---\n\nRelevant documents:\n{context}"
                
                # Generate response
                user_context = None  # TODO: Implement user context from DB
                response_text, generation_time, cumulative_tokens, cumulative_cost = generate_response(
                    request.message,
                    context,
                    user_context=user_context,
                    conversation_history=conversation_context
                )
                status = 'live'
            except Exception as e:
                response_text = f"I encountered an error processing your request: {str(e)}"
                sources = []
                status = 'error'
        else:
            # Coming soon message
            response_text = get_coming_soon_message(domain, request.message)
            sources = []
            status = 'coming-soon'
        
        # Store AI response with patent-ready fields
        assistant_message = crud.create_message(
            db=db,
            session_id=session.session_id,
            role="assistant",
            content=response_text,
            domain=domain,
            confidence=confidence,
            sources=sources,
            status=status,
            retrieval_time=retrieval_time,
            generation_time=generation_time
        )
        
        # Log to Phoenix monitoring
        if monitor and monitor.tracer:
            try:
                monitor.log_query(
                    query=request.message,
                    domain=domain,
                    confidence=confidence,
                    response=response_text,
                    sources=sources,
                    context=context,
                    status=status,
                    retrieval_time=retrieval_time,
                    generation_time=generation_time,
                    cumulative_tokens=cumulative_tokens,
                    cumulative_cost=cumulative_cost,
                    user_id=request.user_id
                )
            except Exception as e:
                print(f"Phoenix logging failed: {e}")
        
        # Prepare source UIDs (patent-ready field)
        source_uids = [f"UID:doc:{hash(src)}" for src in sources] if sources else []
        
        return ChatResponse(
            session_id=session.session_id,
            message_id=assistant_message.message_id,
            response=response_text,
            domain=domain,
            confidence=confidence,
            sources=sources,
            status=status,
            timestamp=assistant_message.timestamp.isoformat(),
            content_hash=assistant_message.content_hash,
            source_document_uids=source_uids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageHistory])
async def get_messages(
    session_id: str,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get message history for a session"""
    try:
        session = crud.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = crud.get_session_messages(db, session_id, limit)
        
        return [
            MessageHistory(
                message_id=msg.message_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                domain=msg.metadata.get('domain') if msg.metadata else None,
                sources=msg.metadata.get('sources') if msg.metadata else None
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db = Depends(get_db)
):
    """Delete a session and all its messages"""
    try:
        success = crud.delete_session(db, session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "success", "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "pinecone": "connected" if os.getenv("PINECONE_API_KEY") else "not configured",
            "cohere": "connected" if os.getenv("COHERE_API_KEY") else "not configured",
            "groq": "connected" if os.getenv("GROQ_API_KEY") else "not configured",
            "phoenix": "connected" if monitor and monitor.tracer else "not configured"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)