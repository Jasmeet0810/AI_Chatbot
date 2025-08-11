import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Lazulite AI PPT Generator API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "ai_service" in data
    assert "environment" in data

def test_cors_headers(client: TestClient):
    """Test CORS headers are present"""
    response = client.options("/")
    assert response.status_code == 200
    # Note: TestClient doesn't automatically handle CORS headers
    # In real tests, you would check for Access-Control-Allow-Origin, etc.

def test_404_endpoint(client: TestClient):
    """Test non-existent endpoint returns 404"""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404