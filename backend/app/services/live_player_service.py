"""In-memory service for live player game state."""

import asyncio
from datetime import UTC, datetime

from app.models.live import Direction, LivePlayer, Position
from app.models.user import GameMode


class LivePlayerService:
    """
    In-memory service for managing live game state.

    This is intentionally not backed by the database as game state
    is ephemeral and updates very frequently (every game tick).
    """

    def __init__(self):
        self._players: dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def add_player(
        self,
        player_id: str,
        user_id: str,
        username: str,
        mode: str,
    ) -> LivePlayer:
        """Add a new live player."""
        async with self._lock:
            player_data = {
                "id": player_id,
                "user_id": user_id,
                "username": username,
                "score": 0,
                "mode": mode,
                "snake": [{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}],
                "food": {"x": 15, "y": 12},
                "direction": "RIGHT",
                "is_alive": True,
                "watcher_count": 0,
                "last_update": datetime.now(UTC),
            }
            self._players[player_id] = player_data

            return self._to_live_player(player_data)

    async def remove_player(self, player_id: str) -> None:
        """Remove a live player."""
        async with self._lock:
            self._players.pop(player_id, None)

    async def get_player(self, player_id: str) -> LivePlayer | None:
        """Get a specific live player."""
        player_data = self._players.get(player_id)
        if not player_data:
            return None
        return self._to_live_player(player_data)

    async def get_all_players(self) -> list[LivePlayer]:
        """Get all live players."""
        return [self._to_live_player(p) for p in self._players.values()]

    async def update_game_state(
        self,
        player_id: str,
        snake: list[dict],
        food: dict,
        direction: str,
        score: int,
        is_alive: bool,
    ) -> None:
        """Update game state for a player."""
        async with self._lock:
            if player_id in self._players:
                player = self._players[player_id]
                player.update(
                    {
                        "snake": snake,
                        "food": food,
                        "direction": direction,
                        "score": score,
                        "is_alive": is_alive,
                        "last_update": datetime.now(UTC),
                    }
                )

    async def increment_watchers(self, player_id: str) -> int | None:
        """Increment watcher count."""
        async with self._lock:
            if player_id in self._players:
                self._players[player_id]["watcher_count"] += 1
                return self._players[player_id]["watcher_count"]
        return None

    async def decrement_watchers(self, player_id: str) -> int | None:
        """Decrement watcher count."""
        async with self._lock:
            if player_id in self._players:
                count = self._players[player_id]["watcher_count"]
                self._players[player_id]["watcher_count"] = max(0, count - 1)
                return self._players[player_id]["watcher_count"]
        return None

    @staticmethod
    def _to_live_player(player_data: dict) -> LivePlayer:
        """Convert internal dict to LivePlayer model."""
        return LivePlayer(
            id=player_data["id"],
            username=player_data["username"],
            score=player_data["score"],
            mode=GameMode(player_data["mode"]),
            snake=[Position(**pos) for pos in player_data["snake"]],
            food=Position(**player_data["food"]),
            direction=Direction(player_data["direction"]),
            isAlive=player_data["is_alive"],
            watcherCount=player_data["watcher_count"],
        )


# Singleton instance
live_player_service = LivePlayerService()
