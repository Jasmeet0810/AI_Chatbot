from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from ..database import get_db, User
from ..auth.utils import get_current_user, get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: str

class UpdateProfile(BaseModel):
    full_name: Optional[str] = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class UserStats(BaseModel):
    total_presentations: int
    total_chat_sessions: int
    account_created: str
    last_activity: Optional[str] = None

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    try:
        return UserProfile(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_update: UpdateProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Update fields if provided
        if profile_update.full_name is not None:
            current_user.full_name = profile_update.full_name.strip()
        
        # Update timestamp
        from datetime import datetime
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.id}")
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post("/change-password")
async def change_password(
    password_change: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_change.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(password_change.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Hash and update password
        current_user.hashed_password = get_password_hash(password_change.new_password)
        
        # Update timestamp
        from datetime import datetime
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.id}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        from ..database import PPTGeneration, ChatSession, Message
        
        # Count presentations
        total_presentations = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).count()
        
        # Count chat sessions
        total_chat_sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).count()
        
        # Get last activity (most recent message or generation)
        last_message = db.query(Message).join(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            Message.sender == "user"
        ).order_by(Message.created_at.desc()).first()
        
        last_generation = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).order_by(PPTGeneration.created_at.desc()).first()
        
        last_activity = None
        if last_message and last_generation:
            last_activity = max(last_message.created_at, last_generation.created_at).isoformat()
        elif last_message:
            last_activity = last_message.created_at.isoformat()
        elif last_generation:
            last_activity = last_generation.created_at.isoformat()
        
        return UserStats(
            total_presentations=total_presentations,
            total_chat_sessions=total_chat_sessions,
            account_created=current_user.created_at.isoformat(),
            last_activity=last_activity
        )
        
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )

@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    try:
        from ..database import PPTGeneration, ChatSession, Message
        import os
        
        # Delete all user's files
        generations = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).all()
        
        for generation in generations:
            if generation.file_path and os.path.exists(generation.file_path):
                try:
                    os.remove(generation.file_path)
                    logger.info(f"Deleted file: {generation.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete file {generation.file_path}: {str(e)}")
        
        # Delete all messages
        chat_sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).all()
        
        for session in chat_sessions:
            db.query(Message).filter(Message.chat_session_id == session.id).delete()
        
        # Delete chat sessions
        db.query(ChatSession).filter(ChatSession.user_id == current_user.id).delete()
        
        # Delete PPT generations
        db.query(PPTGeneration).filter(PPTGeneration.user_id == current_user.id).delete()
        
        # Delete user account
        db.delete(current_user)
        db.commit()
        
        logger.info(f"User account deleted: {current_user.id}")
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete user account: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account"""
    try:
        current_user.is_active = False
        
        from datetime import datetime
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"User account deactivated: {current_user.id}")
        
        return {"message": "Account deactivated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to deactivate account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )

@router.post("/reactivate")
async def reactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate user account"""
    try:
        current_user.is_active = True
        
        from datetime import datetime
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"User account reactivated: {current_user.id}")
        
        return {"message": "Account reactivated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reactivate account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate account"
        )