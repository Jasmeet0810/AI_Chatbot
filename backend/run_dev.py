#!/usr/bin/env python3
"""
Development server runner for Lazulite AI PPT Generator
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Run the development server"""
    
    # Set environment variables for development
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    
    # Create necessary directories
    directories = ["uploads", "generated", "templates", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("🚀 Starting Lazulite AI PPT Generator API...")
    print("📁 Created necessary directories")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\n" + "="*50)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()