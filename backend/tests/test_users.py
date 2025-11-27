"""Tests for user endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestGetUserProfile:
    """Tests for GET /users/{userId}."""

    def test_get_user_profile_success(self, client: TestClient) -> None:
        """Test getting a user profile."""
        response = client.get("/api/v1/users/user-1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user-1"
        assert data["username"] == "SnakeMaster"
        assert data["email"] == "snake@test.com"
        assert "highScore" in data
        assert "gamesPlayed" in data
        assert "createdAt" in data

    def test_get_user_profile_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent user profile."""
        response = client.get("/api/v1/users/nonexistent-user")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "USER_NOT_FOUND"


class TestUpdateUserProfile:
    """Tests for PATCH /users/{userId}."""

    def test_update_user_profile_success(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating own user profile."""
        # First get current user to get the ID
        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"username": "UpdatedName"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "UpdatedName"

    def test_update_user_profile_forbidden(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating another user's profile."""
        response = client.patch(
            "/api/v1/users/user-2",
            json={"username": "HackedName"},
            headers=auth_headers,
        )
        # User-1 is logged in, trying to update user-2
        # This should fail because the mock user 'SnakeMaster' has user-1 as ID
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "FORBIDDEN"

    def test_update_user_profile_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating a non-existent user profile."""
        response = client.patch(
            "/api/v1/users/nonexistent-user",
            json={"username": "NewName"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_update_user_profile_username_taken(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating username to one that's already taken."""
        # Get current user's ID
        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"username": "PyPlayer"},  # Already taken by user-2
            headers=auth_headers,
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "USERNAME_EXISTS"

    def test_update_user_profile_no_auth(self, client: TestClient) -> None:
        """Test updating user profile without authentication."""
        response = client.patch(
            "/api/v1/users/user-1",
            json={"username": "NewName"},
        )
        assert response.status_code == 401

    def test_update_user_profile_invalid_username(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating username with invalid characters."""
        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"username": "Invalid@Name!"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetUserStats:
    """Tests for GET /users/{userId}/stats."""

    def test_get_user_stats_success(self, client: TestClient) -> None:
        """Test getting user stats."""
        response = client.get("/api/v1/users/user-1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "highScore" in data
        assert "gamesPlayed" in data
        assert "rank" in data
        assert data["rank"] >= 1

    def test_get_user_stats_not_found(self, client: TestClient) -> None:
        """Test getting stats for non-existent user."""
        response = client.get("/api/v1/users/nonexistent-user/stats")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "USER_NOT_FOUND"

    def test_get_user_stats_ranking(self, client: TestClient) -> None:
        """Test that user rankings are correct."""
        # User-1 has highest score (1500), should be rank 1
        response1 = client.get("/api/v1/users/user-1/stats")
        assert response1.json()["rank"] == 1

        # User-2 has second highest score (1200), should be rank 2
        response2 = client.get("/api/v1/users/user-2/stats")
        assert response2.json()["rank"] == 2

        # User-3 has lowest score (800), should be rank 3
        response3 = client.get("/api/v1/users/user-3/stats")
        assert response3.json()["rank"] == 3
