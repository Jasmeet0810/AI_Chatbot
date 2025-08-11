import pytest
from fastapi.testclient import TestClient

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user(self, client: TestClient, test_user_data: dict):
        """Test user registration"""
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/auth/register", json=test_user_data)
        
        # Try to register again with same email
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "TestPassword123!"
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        weak_password_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "weak"
        }
        
        response = client.post("/auth/register", json=weak_password_data)
        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Test successful login"""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_user_data: dict):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Try login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrong_password"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test getting current user info"""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401