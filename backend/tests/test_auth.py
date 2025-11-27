"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestLogin:
    """Tests for POST /auth/login."""

    def test_login_success(self, client: TestClient) -> None:
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "snake@test.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == "snake@test.com"
        assert data["user"]["username"] == "SnakeMaster"
        assert "highScore" in data["user"]
        assert "gamesPlayed" in data["user"]
        assert "createdAt" in data["user"]

    def test_login_invalid_email(self, client: TestClient) -> None:
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "password123"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "INVALID_CREDENTIALS"

    def test_login_invalid_password(self, client: TestClient) -> None:
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "snake@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "INVALID_CREDENTIALS"

    def test_login_invalid_email_format(self, client: TestClient) -> None:
        """Test login with invalid email format."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "notanemail", "password": "password123"},
        )
        assert response.status_code == 422  # Validation error

    def test_login_short_password(self, client: TestClient) -> None:
        """Test login with password shorter than minimum."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "snake@test.com", "password": "abc"},
        )
        assert response.status_code == 422  # Validation error


class TestSignup:
    """Tests for POST /auth/signup."""

    def test_signup_success(self, client: TestClient) -> None:
        """Test successful signup."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "NewPlayer",
                "email": "newplayer@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["username"] == "NewPlayer"
        assert data["user"]["email"] == "newplayer@test.com"
        assert data["user"]["highScore"] == 0
        assert data["user"]["gamesPlayed"] == 0

    def test_signup_duplicate_email(self, client: TestClient) -> None:
        """Test signup with existing email."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "AnotherUser",
                "email": "snake@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "EMAIL_EXISTS"

    def test_signup_duplicate_username(self, client: TestClient) -> None:
        """Test signup with existing username."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "SnakeMaster",
                "email": "another@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "USERNAME_EXISTS"

    def test_signup_invalid_username_characters(self, client: TestClient) -> None:
        """Test signup with invalid username characters."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "User@Name!",
                "email": "test@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_signup_username_too_short(self, client: TestClient) -> None:
        """Test signup with username shorter than minimum."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "ab",
                "email": "test@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_signup_username_too_long(self, client: TestClient) -> None:
        """Test signup with username longer than maximum."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "username": "a" * 31,
                "email": "test@test.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422


class TestLogout:
    """Tests for POST /auth/logout."""

    def test_logout_success(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Test successful logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_logout_invalidates_token(self, client: TestClient) -> None:
        """Test that logout invalidates the token."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "snake@test.com", "password": "password123"},
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Logout
        client.post("/api/v1/auth/logout", headers=headers)

        # Try to access protected endpoint with same token
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_logout_no_auth(self, client: TestClient) -> None:
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401  # No bearer token provided


class TestGetCurrentUser:
    """Tests for GET /auth/me."""

    def test_get_current_user_success(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting current user."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "snake@test.com"
        assert data["username"] == "SnakeMaster"
        assert "id" in data
        assert "highScore" in data
        assert "gamesPlayed" in data
        assert "createdAt" in data

    def test_get_current_user_no_auth(self, client: TestClient) -> None:
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient) -> None:
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401
