"""Tests for leaderboard endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestGetLeaderboard:
    """Tests for GET /leaderboard."""

    def test_get_leaderboard_default(self, client: TestClient) -> None:
        """Test getting leaderboard with default parameters."""
        response = client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # Default limit

        # Check structure of entries
        for entry in data:
            assert "id" in entry
            assert "username" in entry
            assert "score" in entry
            assert "mode" in entry
            assert "date" in entry

    def test_get_leaderboard_sorted_by_score(self, client: TestClient) -> None:
        """Test that leaderboard is sorted by score descending."""
        response = client.get("/api/v1/leaderboard")
        data = response.json()
        scores = [entry["score"] for entry in data]
        assert scores == sorted(scores, reverse=True)

    def test_get_leaderboard_with_limit(self, client: TestClient) -> None:
        """Test getting leaderboard with custom limit."""
        response = client.get("/api/v1/leaderboard?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_leaderboard_filter_by_mode_walls(self, client: TestClient) -> None:
        """Test filtering leaderboard by walls mode."""
        response = client.get("/api/v1/leaderboard?mode=walls")
        assert response.status_code == 200
        data = response.json()
        for entry in data:
            assert entry["mode"] == "walls"

    def test_get_leaderboard_filter_by_mode_pass_through(self, client: TestClient) -> None:
        """Test filtering leaderboard by pass-through mode."""
        response = client.get("/api/v1/leaderboard?mode=pass-through")
        assert response.status_code == 200
        data = response.json()
        for entry in data:
            assert entry["mode"] == "pass-through"

    def test_get_leaderboard_invalid_limit_too_low(self, client: TestClient) -> None:
        """Test getting leaderboard with limit below minimum."""
        response = client.get("/api/v1/leaderboard?limit=0")
        assert response.status_code == 422

    def test_get_leaderboard_invalid_limit_too_high(self, client: TestClient) -> None:
        """Test getting leaderboard with limit above maximum."""
        response = client.get("/api/v1/leaderboard?limit=101")
        assert response.status_code == 422


class TestSubmitScore:
    """Tests for POST /leaderboard/scores."""

    def test_submit_score_success(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test submitting a score."""
        response = client.post(
            "/api/v1/leaderboard/scores",
            json={"score": 500, "mode": "walls"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 500
        assert data["mode"] == "walls"
        assert data["username"] == "SnakeMaster"
        assert "id" in data
        assert "date" in data

    def test_submit_score_updates_user_stats(
        self, client: TestClient, new_user_auth_headers: dict[str, str]
    ) -> None:
        """Test that submitting a score updates user stats."""
        # Get current user
        me_response = client.get("/api/v1/auth/me", headers=new_user_auth_headers)
        user_id = me_response.json()["id"]
        initial_games = me_response.json()["gamesPlayed"]

        # Submit a score
        client.post(
            "/api/v1/leaderboard/scores",
            json={"score": 1000, "mode": "walls"},
            headers=new_user_auth_headers,
        )

        # Check stats were updated
        stats_response = client.get(f"/api/v1/users/{user_id}/stats")
        stats = stats_response.json()
        assert stats["gamesPlayed"] == initial_games + 1
        assert stats["highScore"] == 1000

    def test_submit_score_no_auth(self, client: TestClient) -> None:
        """Test submitting a score without authentication."""
        response = client.post(
            "/api/v1/leaderboard/scores",
            json={"score": 500, "mode": "walls"},
        )
        assert response.status_code == 401

    def test_submit_score_negative(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test submitting a negative score."""
        response = client.post(
            "/api/v1/leaderboard/scores",
            json={"score": -100, "mode": "walls"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_submit_score_invalid_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test submitting a score with invalid mode."""
        response = client.post(
            "/api/v1/leaderboard/scores",
            json={"score": 500, "mode": "invalid-mode"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_submit_score_pass_through_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test submitting a score with pass-through mode."""
        response = client.post(
            "/api/v1/leaderboard/scores",
            json={"score": 750, "mode": "pass-through"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "pass-through"


class TestGetUserRank:
    """Tests for GET /leaderboard/rank/{userId}."""

    def test_get_user_rank_success(self, client: TestClient) -> None:
        """Test getting user rank."""
        response = client.get("/api/v1/leaderboard/rank/user-1")
        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == "user-1"
        assert data["rank"] >= 1

    def test_get_user_rank_not_found(self, client: TestClient) -> None:
        """Test getting rank for non-existent user."""
        response = client.get("/api/v1/leaderboard/rank/nonexistent-user")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "USER_NOT_FOUND"

    def test_get_user_rank_correct_order(self, client: TestClient) -> None:
        """Test that user ranks are in correct order."""
        # User-1 has highest score (1500), should be rank 1
        response1 = client.get("/api/v1/leaderboard/rank/user-1")
        assert response1.json()["rank"] == 1

        # User-2 has second highest score (1200), should be rank 2
        response2 = client.get("/api/v1/leaderboard/rank/user-2")
        assert response2.json()["rank"] == 2

        # User-3 has lowest score (800), should be rank 3
        response3 = client.get("/api/v1/leaderboard/rank/user-3")
        assert response3.json()["rank"] == 3
