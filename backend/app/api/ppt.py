from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ..ppt.generator import PPTGenerator
from ..ppt.templates import PPTTemplateManager
import logging
import uuid
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class PPTRequest(BaseModel):
    prompt: str
    approved_content: List[Dict[str, Any]]
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

# In-memory storage for demo (replace with proper storage in production)
task_storage = {}

@router.post("/generate", response_model=PPTResponse)
async def generate_presentation(request: PPTRequest):
    """Generate PPT from user prompt and approved content"""
    try:
        logger.info("PPT generation requested")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Store task status
        task_storage[task_id] = {
            "status": "processing",
            "progress": "Starting PPT generation...",
            "download_url": None,
            "error_message": None
        }
        
        try:
            # Initialize template manager and generator
            template_manager = PPTTemplateManager()
            template_path = template_manager.ensure_template_exists()
            
            generator = PPTGenerator(template_path)
            
            # Generate PPT with approved content
            ppt_path = generator.generate_presentation(
                request.approved_content, 
                request.prompt,
                user_id="demo_user"
            )
            
            # Generate download URL
            filename = os.path.basename(ppt_path)
            download_url = f"/static/{filename}"
            
            # Update task status
            task_storage[task_id] = {
                "status": "completed",
                "progress": "PPT generation completed successfully",
                "download_url": download_url,
                "error_message": None
            }
            
            logger.info(f"PPT generation completed successfully: {ppt_path}")
            
        except Exception as e:
            logger.error(f"PPT generation failed: {str(e)}")
            task_storage[task_id] = {
                "status": "failed",
                "progress": "PPT generation failed",
                "download_url": None,
                "error_message": str(e)
            }
        
        return PPTResponse(
            task_id=task_id,
            status="processing",
            message="PPT generation started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start PPT generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start PPT generation"
        )

@router.get("/status/{task_id}", response_model=PPTStatusResponse)
async def get_generation_status(task_id: str):
    """Get PPT generation status"""
    try:
        if task_id not in task_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task_info = task_storage[task_id]
        
        return PPTStatusResponse(
            task_id=task_id,
            status=task_info["status"],
            progress=task_info["progress"],
            download_url=task_info["download_url"],
            error_message=task_info["error_message"]
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
async def download_presentation(filename: str):
    """Download generated presentation"""
    try:
        from fastapi.responses import FileResponse
        from ..config import settings
        
        # Construct file path
        file_path = os.path.join(settings.generated_dir, filename)
        
        # Verify file exists
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
        
        logger.info(f"File download requested: {filename}")
        
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