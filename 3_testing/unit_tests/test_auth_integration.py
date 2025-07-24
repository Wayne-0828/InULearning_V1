import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import UserRole

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "student",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "testpassword123",
            "role": "student"
        }
        
        # Register first user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Try to register with same email
        user_data["username"] = "user2"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login"""
        # Register user first
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpassword123",
            "role": "student"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_refresh_token(self):
        """Test token refresh"""
        # Register and login user
        user_data = {
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "testpassword123",
            "role": "student"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "refresh@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
    
    def test_logout(self):
        """Test logout"""
        # Register and login user
        user_data = {
            "email": "logout@example.com",
            "username": "logoutuser",
            "password": "testpassword123",
            "role": "student"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "logout@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        logout_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/logout", json=logout_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"


class TestUsers:
    """Test user management endpoints"""
    
    def test_get_profile(self):
        """Test getting user profile"""
        # Register and login user
        user_data = {
            "email": "profile@example.com",
            "username": "profileuser",
            "password": "testpassword123",
            "role": "student"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "profile@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "profile@example.com"
        assert response.json()["username"] == "profileuser"
    
    def test_update_profile(self):
        """Test updating user profile"""
        # Register and login user
        user_data = {
            "email": "update@example.com",
            "username": "updateuser",
            "password": "testpassword123",
            "role": "student"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "update@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"
        assert response.json()["last_name"] == "Name" 