from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db, User, ChatSession, Message
from ..auth.utils import get_current_user
from ..ai.content_generator import ContentGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    id: str
    content: str
    sender: str
    timestamp: datetime
    ppt_download_url: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

class ChatHistoryResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int

# Initialize content generator
content_generator = ContentGenerator()

@router.post("/sessions", response_model=dict)
async def create_chat_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        # Create new chat session
        chat_session = ChatSession(
            user_id=current_user.id,
            title="New Chat"
        )
        
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        
        # Add welcome message
        welcome_message = Message(
            chat_session_id=chat_session.id,
            content="Hello! I'm the Lazulite AI PPT Generator. I can create professional presentations from your prompts using data extracted from Lazulite products. Just describe what kind of presentation you need!",
            sender="ai"
        )
        
        db.add(welcome_message)
        db.commit()
        
        logger.info(f"Created new chat session: {chat_session.id}")
        
        return {
            "session_id": str(chat_session.id),
            "message": "Chat session created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )

@router.get("/sessions", response_model=ChatHistoryResponse)
async def get_chat_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    try:
        # Get chat sessions with message count
        sessions_query = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(ChatSession.updated_at.desc())
        
        total = sessions_query.count()
        sessions = sessions_query.offset(offset).limit(limit).all()
        
        # Build response with message counts
        session_responses = []
        for session in sessions:
            message_count = db.query(Message).filter(
                Message.chat_session_id == session.id
            ).count()
            
            session_responses.append(ChatSessionResponse(
                id=str(session.id),
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count
            ))
        
        return ChatHistoryResponse(
            sessions=session_responses,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Failed to get chat sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat sessions"
        )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatResponse])
async def get_chat_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a chat session"""
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        messages = db.query(Message).filter(
            Message.chat_session_id == session_id
        ).order_by(Message.created_at.asc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        message_responses = []
        for message in messages:
            message_responses.append(ChatResponse(
                id=str(message.id),
                content=message.content,
                sender=message.sender,
                timestamp=message.created_at,
                ppt_download_url=message.ppt_download_url
            ))
        
        return message_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session"""
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Save user message
        user_message = Message(
            chat_session_id=session_id,
            content=message.content,
            sender="user"
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Generate AI response
        try:
            ai_response_content = content_generator.generate_chat_response(
                message.content,
                context={"session_id": session_id, "user_id": str(current_user.id)}
            )
        except Exception as e:
            logger.warning(f"AI response generation failed: {str(e)}")
            ai_response_content = "I understand your request. Let me help you create a professional presentation based on Lazulite product data."
        
        # Save AI response
        ai_message = Message(
            chat_session_id=session_id,
            content=ai_response_content,
            sender="ai"
        )
        
        db.add(ai_message)
        
        # Update session title if it's the first user message
        if session.title == "New Chat":
            # Generate title from first message
            title = message.content[:50] + "..." if len(message.content) > 50 else message.content
            session.title = title
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ai_message)
        
        logger.info(f"Message sent in session {session_id}")
        
        return ChatResponse(
            id=str(ai_message.id),
            content=ai_message.content,
            sender=ai_message.sender,
            timestamp=ai_message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Delete all messages in the session
        db.query(Message).filter(Message.chat_session_id == session_id).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        logger.info(f"Deleted chat session: {session_id}")
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )

@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update chat session title"""
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Update title
        session.title = title[:100]  # Limit title length
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Session title updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session title: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session title"
        )