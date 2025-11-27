"""Tests for live players endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestGetLivePlayers:
    """Tests for GET /live/players."""

    def test_get_live_players_success(self, client: TestClient) -> None:
        """Test getting list of live players."""
        response = client.get("/api/v1/live/players")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Check structure if there are players
        for player in data:
            assert "id" in player
            assert "username" in player
            assert "score" in player
            assert "mode" in player
            assert "snake" in player
            assert "food" in player
            assert "direction" in player
            assert "isAlive" in player
            assert "watcherCount" in player


class TestGetLivePlayer:
    """Tests for GET /live/players/{playerId}."""

    def test_get_live_player_success(self, client: TestClient) -> None:
        """Test getting a specific live player."""
        response = client.get("/api/v1/live/players/live-1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "live-1"
        assert data["username"] == "PyPlayer"
        assert "score" in data
        assert "mode" in data
        assert "snake" in data
        assert isinstance(data["snake"], list)
        assert "food" in data
        assert "x" in data["food"]
        assert "y" in data["food"]
        assert "direction" in data
        assert "isAlive" in data
        assert "watcherCount" in data

    def test_get_live_player_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent live player."""
        response = client.get("/api/v1/live/players/nonexistent-player")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "PLAYER_NOT_FOUND"


class TestJoinAsWatcher:
    """Tests for POST /live/players/{playerId}/watch."""

    def test_join_as_watcher_success(self, client: TestClient) -> None:
        """Test joining as a watcher."""
        # Get initial watcher count
        initial_response = client.get("/api/v1/live/players/live-1")
        initial_count = initial_response.json()["watcherCount"]

        response = client.post("/api/v1/live/players/live-1/watch")
        assert response.status_code == 200
        data = response.json()
        assert "watcherCount" in data
        assert data["watcherCount"] == initial_count + 1

    def test_join_as_watcher_not_found(self, client: TestClient) -> None:
        """Test joining as watcher for non-existent player."""
        response = client.post("/api/v1/live/players/nonexistent-player/watch")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "PLAYER_NOT_FOUND"


class TestLeaveAsWatcher:
    """Tests for DELETE /live/players/{playerId}/watch."""

    def test_leave_as_watcher_success(self, client: TestClient) -> None:
        """Test leaving as a watcher."""
        # First join as watcher
        client.post("/api/v1/live/players/live-1/watch")

        # Get current watcher count
        current_response = client.get("/api/v1/live/players/live-1")
        current_count = current_response.json()["watcherCount"]

        # Leave as watcher
        response = client.delete("/api/v1/live/players/live-1/watch")
        assert response.status_code == 200
        data = response.json()
        assert "watcherCount" in data
        assert data["watcherCount"] == current_count - 1

    def test_leave_as_watcher_not_found(self, client: TestClient) -> None:
        """Test leaving as watcher for non-existent player."""
        response = client.delete("/api/v1/live/players/nonexistent-player/watch")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "PLAYER_NOT_FOUND"

    def test_leave_as_watcher_minimum_zero(self, client: TestClient) -> None:
        """Test that watcher count doesn't go below zero."""
        # Leave multiple times
        for _ in range(10):
            client.delete("/api/v1/live/players/live-1/watch")

        response = client.get("/api/v1/live/players/live-1")
        data = response.json()
        assert data["watcherCount"] >= 0


class TestWebSocketStream:
    """Tests for WebSocket /live/players/{playerId}/stream."""

    def test_websocket_connection_success(self, client: TestClient) -> None:
        """Test WebSocket connection to live player stream."""
        with client.websocket_connect("/api/v1/live/players/live-1/stream") as websocket:
            # Should receive initial game state
            data = websocket.receive_json()
            assert data["type"] == "gameState"
            assert "data" in data
            assert "snake" in data["data"]
            assert "food" in data["data"]
            assert "direction" in data["data"]
            assert "score" in data["data"]
            assert "isAlive" in data["data"]

    def test_websocket_player_not_found(self, client: TestClient) -> None:
        """Test WebSocket connection to non-existent player."""
        with pytest.raises(Exception):
            # Should fail to connect
            with client.websocket_connect("/api/v1/live/players/nonexistent/stream"):
                pass
