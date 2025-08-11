#!/usr/bin/env python3
"""
Celery beat scheduler runner for development
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Run the Celery beat scheduler"""
    
    # Set environment variables for development
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    
    print("⏰ Starting Celery Beat Scheduler...")
    print("📅 Managing periodic tasks")
    print("\n" + "="*50)
    
    # Import and run celery beat
    from app.tasks.celery_app import celery_app
    
    celery_app.worker_main([
        'beat',
        '--loglevel=info'
    ])

if __name__ == "__main__":
    main()