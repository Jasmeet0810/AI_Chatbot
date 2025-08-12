from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging

from .api.extract import router as extract_router
from .api.ppt import router as ppt_router
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
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extract_router, prefix="/api", tags=["content-extraction"])
app.include_router(ppt_router, prefix="/api/ppt", tags=["presentations"])

# Mount static files
if os.path.exists(settings.generated_dir):
    app.mount("/static", StaticFiles(directory=settings.generated_dir), name="static")

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
        # Check AI service
        from .ai.bedrock_service import bedrock_service
        ai_status = "healthy" if bedrock_service.is_available() else "unavailable"
    except Exception as e:
        ai_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
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