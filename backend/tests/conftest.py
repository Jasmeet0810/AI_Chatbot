import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create test client"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create database session for testing"""
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "TestPassword123!"
    }

@pytest.fixture
def test_ppt_request():
    """Test PPT generation request"""
    return {
        "prompt": "Create a presentation about AI Photobooth features and specifications",
        "product_url": "https://lazulite.ae/activations"
    }

@pytest.fixture
def test_chat_message():
    """Test chat message"""
    return {
        "content": "I want to create a presentation about digital kiosks"
    }

@pytest.fixture
def auth_headers(client: TestClient, test_user_data: dict):
    """Get authentication headers for testing"""
    # Register user
    client.post("/auth/register", json=test_user_data)
    
    # Login and get token
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Mock configurations for testing
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock settings for testing"""
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(settings, "environment", "testing")
    monkeypatch.setattr(settings, "debug", True)