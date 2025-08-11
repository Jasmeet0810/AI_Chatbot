from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import logging

from .auth.routes import router as auth_router
from .api.chat import router as chat_router
from .api.ppt import router as ppt_router
from .api.user import router as user_router
from .database import create_tables, get_db
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lazulite AI PPT Generator API",
    version="1.0.0",
    description="AI-powered PowerPoint generation from Lazulite product data"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(ppt_router, prefix="/api/ppt", tags=["presentations"])
app.include_router(user_router, prefix="/api/user", tags=["user"])

# Mount static files
app.mount("/static", StaticFiles(directory="generated"), name="static")

class PPTRequest(BaseModel):
    prompt: str
    product_url: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lazulite AI PPT Generator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check AI service
    try:
        from .ai.langchain_service import langchain_service
        ai_status = "healthy" if langchain_service.is_available() else "unavailable"
    except Exception as e:
        ai_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "ai_service": ai_status,
        "environment": settings.environment
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Lazulite AI PPT Generator API")
    
    # Ensure directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.generated_dir, exist_ok=True)
    os.makedirs(settings.template_dir, exist_ok=True)
    
    logger.info("API startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Lazulite AI PPT Generator API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )