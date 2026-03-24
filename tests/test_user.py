import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.services.user_service import UserService


client = TestClient(app)


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    def test_register_user_success(self):
        """Test successful user registration."""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User"
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert data["full_name"] == payload["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Ensure password is not in response

    def test_register_user_minimal(self):
        """Test user registration with minimal required fields."""
        payload = {
            "email": "minimal@example.com",
            "username": "minimal_user",
            "password": "minimalpass123"
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert data["full_name"] is None

    def test_register_user_duplicate_email(self):
        """Test registration fails when email already exists."""
        # Register first user
        payload1 = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        client.post("/users/register", json=payload1)

        # Try to register with same email
        payload2 = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password456"
        }
        response = client.post("/users/register", json=payload2)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "already exists" in data["detail"].lower()

    def test_register_user_duplicate_username(self):
        """Test registration fails when username already exists."""
        # Register first user
        payload1 = {
            "email": "user1@example.com",
            "username": "duplicate_user",
            "password": "password123"
        }
        client.post("/users/register", json=payload1)

        # Try to register with same username
        payload2 = {
            "email": "user2@example.com",
            "username": "duplicate_user",
            "password": "password456"
        }
        response = client.post("/users/register", json=payload2)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "already taken" in data["detail"].lower()

    def test_register_user_invalid_email(self):
        """Test registration fails with invalid email format."""
        payload = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "password123"
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_short_password(self):
        """Test registration fails when password is too short."""
        payload = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short"  # Less than 8 characters
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_short_username(self):
        """Test registration fails when username is too short."""
        payload = {
            "email": "test@example.com",
            "username": "ab",  # Less than 3 characters
            "password": "password123"
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_missing_required_field(self):
        """Test registration fails when required fields are missing."""
        payload = {
            "email": "test@example.com",
            "username": "testuser"
            # Missing password
        }

        response = client.post("/users/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserService:
    """Test cases for UserService business logic."""

    def test_service_register_user(self):
        """Test UserService.register_user()."""
        service = UserService()

        result = service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["username"] == "testuser"
        assert result["full_name"] == "Test User"
        assert "password_hash" not in result

    def test_service_register_duplicate_email_raises_error(self):
        """Test UserService raises error on duplicate email."""
        service = UserService()

        service.register_user(
            email="test@example.com",
            username="user1",
            password="password123"
        )

        with pytest.raises(ValueError, match="already registered"):
            service.register_user(
                email="test@example.com",
                username="user2",
                password="password456"
            )

    def test_service_register_duplicate_username_raises_error(self):
        """Test UserService raises error on duplicate username."""
        service = UserService()

        service.register_user(
            email="user1@example.com",
            username="testuser",
            password="password123"
        )

        with pytest.raises(ValueError, match="already taken"):
            service.register_user(
                email="user2@example.com",
                username="testuser",
                password="password456"
            )

    def test_service_get_user_by_id(self):
        """Test UserService.get_user_by_id()."""
        service = UserService()

        service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )

        user = service.get_user_by_id(1)
        assert user is not None
        assert user["email"] == "test@example.com"

    def test_service_get_user_by_email(self):
        """Test UserService.get_user_by_email()."""
        service = UserService()

        service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )

        user = service.get_user_by_email("test@example.com")
        assert user is not None
        assert user["username"] == "testuser"

    def test_service_verify_password_success(self):
        """Test UserService.verify_password() with correct password."""
        service = UserService()

        service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )

        assert service.verify_password("test@example.com", "password123") is True

    def test_service_verify_password_failure(self):
        """Test UserService.verify_password() with incorrect password."""
        service = UserService()

        service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )

        assert service.verify_password("test@example.com", "wrongpassword") is False
