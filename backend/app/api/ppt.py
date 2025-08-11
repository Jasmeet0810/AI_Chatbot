from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from ..database import get_db, User, PPTGeneration
from ..auth.utils import get_current_user
from ..tasks.ppt_tasks import generate_ppt_task
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class PPTRequest(BaseModel):
    prompt: str
    product_url: Optional[str] = None
    template: Optional[str] = None

class PPTResponse(BaseModel):
    task_id: str
    status: str
    message: str

class PPTStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

@router.post("/generate", response_model=PPTResponse)
async def generate_presentation(
    request: PPTRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PPT from user prompt"""
    try:
        logger.info(f"PPT generation requested by user {current_user.id}")
        
        # Create PPT generation record
        ppt_generation = PPTGeneration(
            user_id=current_user.id,
            prompt=request.prompt,
            product_url=request.product_url,
            status="pending"
        )
        
        db.add(ppt_generation)
        db.commit()
        db.refresh(ppt_generation)
        
        # Start background task
        task = generate_ppt_task.delay(
            generation_id=str(ppt_generation.id),
            user_id=str(current_user.id),
            prompt=request.prompt,
            product_url=request.product_url or "https://lazulite.ae/activations",
            template=request.template
        )
        
        # Update generation record with task ID
        ppt_generation.status = "processing"
        db.commit()
        
        logger.info(f"PPT generation task started: {task.id}")
        
        return PPTResponse(
            task_id=task.id,
            status="processing",
            message="PPT generation started. This may take a few minutes."
        )
        
    except Exception as e:
        logger.error(f"Failed to start PPT generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start PPT generation"
        )

@router.get("/status/{task_id}", response_model=PPTStatusResponse)
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PPT generation status"""
    try:
        # Get task result
        from ..tasks.celery_app import celery_app
        task_result = celery_app.AsyncResult(task_id)
        
        # Find corresponding generation record
        generation = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).order_by(PPTGeneration.created_at.desc()).first()
        
        if not generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation record not found"
            )
        
        # Determine status
        if task_result.state == 'PENDING':
            status_text = "pending"
            progress = "Task is waiting to be processed"
        elif task_result.state == 'PROGRESS':
            status_text = "processing"
            progress = task_result.info.get('progress', 'Processing...')
        elif task_result.state == 'SUCCESS':
            status_text = "completed"
            progress = "Completed successfully"
        elif task_result.state == 'FAILURE':
            status_text = "failed"
            progress = "Generation failed"
        else:
            status_text = task_result.state.lower()
            progress = f"Status: {task_result.state}"
        
        # Get result data if completed
        download_url = None
        error_message = None
        
        if task_result.state == 'SUCCESS' and task_result.result:
            result = task_result.result
            if isinstance(result, dict):
                download_url = result.get('download_url')
        elif task_result.state == 'FAILURE':
            error_message = str(task_result.info)
        
        return PPTStatusResponse(
            task_id=task_id,
            status=status_text,
            progress=progress,
            download_url=download_url,
            error_message=error_message,
            created_at=generation.created_at.isoformat(),
            completed_at=generation.completed_at.isoformat() if generation.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get generation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get generation status"
        )

@router.get("/download/{filename}")
async def download_presentation(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download generated presentation"""
    try:
        from fastapi.responses import FileResponse
        from ..config import settings
        import os
        
        # Construct file path
        file_path = os.path.join(settings.generated_dir, filename)
        
        # Verify file exists and belongs to user
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Security check: ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        logger.info(f"File download requested: {filename} by user {current_user.id}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )

@router.get("/history")
async def get_generation_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's PPT generation history"""
    try:
        generations = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).order_by(PPTGeneration.created_at.desc()).offset(offset).limit(limit).all()
        
        total = db.query(PPTGeneration).filter(
            PPTGeneration.user_id == current_user.id
        ).count()
        
        history = []
        for gen in generations:
            history.append({
                "id": str(gen.id),
                "prompt": gen.prompt,
                "status": gen.status,
                "created_at": gen.created_at.isoformat(),
                "completed_at": gen.completed_at.isoformat() if gen.completed_at else None,
                "file_path": gen.file_path,
                "error_message": gen.error_message
            })
        
        return {
            "history": history,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get generation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get generation history"
        )

@router.delete("/history/{generation_id}")
async def delete_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a PPT generation record and file"""
    try:
        generation = db.query(PPTGeneration).filter(
            PPTGeneration.id == generation_id,
            PPTGeneration.user_id == current_user.id
        ).first()
        
        if not generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation record not found"
            )
        
        # Delete file if it exists
        if generation.file_path and os.path.exists(generation.file_path):
            try:
                os.remove(generation.file_path)
                logger.info(f"Deleted file: {generation.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {generation.file_path}: {str(e)}")
        
        # Delete database record
        db.delete(generation)
        db.commit()
        
        return {"message": "Generation record deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete generation"
        )