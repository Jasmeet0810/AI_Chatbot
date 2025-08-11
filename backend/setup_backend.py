#!/usr/bin/env python3
"""
Setup script for Lazulite AI PPT Generator Backend
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_requirements():
    """Check if required software is installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'postgresql': 'psql --version',
        'redis': 'redis-server --version'
    }
    
    missing = []
    for name, command in requirements.items():
        if not run_command(command, f"Checking {name}"):
            missing.append(name)
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        print("\nPlease install the missing requirements:")
        print("- Python 3.9+: https://python.org")
        print("- PostgreSQL: https://postgresql.org")
        print("- Redis: https://redis.io")
        return False
    
    return True

def setup_environment():
    """Setup Python virtual environment"""
    print("🐍 Setting up Python environment...")
    
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            return False
    
    # Activate virtual environment and install requirements
    if sys.platform == 'win32':
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
    else:
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
    
    if not run_command(f'{pip_cmd} install --upgrade pip', 'Upgrading pip'):
        return False
    
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Installing Python packages'):
        return False
    
    return True

def setup_database():
    """Setup PostgreSQL database"""
    print("🗄️ Setting up database...")
    
    # Create database
    db_commands = [
        'createdb lazulite_ppt',
        'psql -d lazulite_ppt -c "CREATE EXTENSION IF NOT EXISTS uuid-ossp;"'
    ]
    
    for cmd in db_commands:
        run_command(cmd, f"Running: {cmd}")
    
    return True

def setup_configuration():
    """Setup configuration files"""
    print("⚙️ Setting up configuration...")
    
    # Copy environment file
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("❌ .env.example not found")
            return False
    
    # Create directories
    directories = ['uploads', 'generated', 'templates', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    
    if sys.platform == 'win32':
        alembic_cmd = 'venv\\Scripts\\alembic'
    else:
        alembic_cmd = 'venv/bin/alembic'
    
    return run_command(f'{alembic_cmd} upgrade head', 'Running migrations')

def main():
    """Main setup function"""
    print("🚀 Setting up Lazulite AI PPT Generator Backend")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    steps = [
        ("Checking requirements", check_requirements),
        ("Setting up environment", setup_environment),
        ("Setting up configuration", setup_configuration),
        ("Setting up database", setup_database),
        ("Running migrations", run_migrations),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Backend setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Start Redis: redis-server")
    print("3. Start the API: python run_dev.py")
    print("4. Start the worker: python run_worker.py")
    print("5. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()