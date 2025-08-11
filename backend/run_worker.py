#!/usr/bin/env python3
"""
Celery worker runner for development
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Run the Celery worker"""
    
    # Set environment variables for development
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    
    print("🔄 Starting Celery Worker...")
    print("📋 Processing background tasks for PPT generation")
    print("\n" + "="*50)
    
    # Import and run celery worker
    from app.tasks.celery_app import celery_app
    
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=solo' if sys.platform == 'win32' else '--pool=prefork'
    ])

if __name__ == "__main__":
    main()