"""Mock in-memory database for development and testing."""

from datetime import UTC, datetime
from typing import TypedDict
from uuid import uuid4

from app.models.leaderboard import LeaderboardEntry
from app.models.live import Direction, LivePlayer, Position
from app.models.user import GameMode, User
from app.services.auth import get_password_hash


class UserRecord(TypedDict):
    """Internal user record with password hash."""

    id: str
    username: str
    email: str
    password_hash: str
    high_score: int
    games_played: int
    created_at: datetime


class LeaderboardRecord(TypedDict):
    """Internal leaderboard record."""

    id: str
    user_id: str
    username: str
    score: int
    mode: str
    date: datetime


class LivePlayerRecord(TypedDict):
    """Internal live player record."""

    id: str
    user_id: str
    username: str
    score: int
    mode: str
    snake: list[dict[str, int]]
    food: dict[str, int]
    direction: str
    is_alive: bool
    watcher_count: int


class MockDatabase:
    """In-memory mock database."""

    def __init__(self) -> None:
        self.users: dict[str, UserRecord] = {}
        self.leaderboard: dict[str, LeaderboardRecord] = {}
        self.live_players: dict[str, LivePlayerRecord] = {}
        self.invalidated_tokens: set[str] = set()
        self._seed_data()

    def _seed_data(self) -> None:
        """Seed the database with initial test data."""
        # Create some test users
        users_data = [
            {
                "id": "user-1",
                "username": "SnakeMaster",
                "email": "snake@test.com",
                "password": "password123",
                "high_score": 1500,
                "games_played": 42,
            },
            {
                "id": "user-2",
                "username": "PyPlayer",
                "email": "python@test.com",
                "password": "password123",
                "high_score": 1200,
                "games_played": 30,
            },
            {
                "id": "user-3",
                "username": "GamePro",
                "email": "pro@test.com",
                "password": "password123",
                "high_score": 800,
                "games_played": 15,
            },
        ]

        for user_data in users_data:
            self.users[user_data["id"]] = UserRecord(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                high_score=user_data["high_score"],
                games_played=user_data["games_played"],
                created_at=datetime.now(UTC),
            )

        # Create some leaderboard entries
        leaderboard_data = [
            {"user_id": "user-1", "username": "SnakeMaster", "score": 1500, "mode": "walls"},
            {"user_id": "user-2", "username": "PyPlayer", "score": 1200, "mode": "walls"},
            {"user_id": "user-1", "username": "SnakeMaster", "score": 1100, "mode": "pass-through"},
            {"user_id": "user-3", "username": "GamePro", "score": 800, "mode": "walls"},
        ]

        for entry_data in leaderboard_data:
            entry_id = str(uuid4())
            self.leaderboard[entry_id] = LeaderboardRecord(
                id=entry_id,
                user_id=entry_data["user_id"],
                username=entry_data["username"],
                score=entry_data["score"],
                mode=entry_data["mode"],
                date=datetime.now(UTC),
            )

        # Create a live player for testing
        self.live_players["live-1"] = LivePlayerRecord(
            id="live-1",
            user_id="user-2",
            username="PyPlayer",
            score=340,
            mode="walls",
            snake=[{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}],
            food={"x": 15, "y": 12},
            direction="RIGHT",
            is_alive=True,
            watcher_count=2,
        )

    def reset(self) -> None:
        """Reset the database to initial state."""
        self.users.clear()
        self.leaderboard.clear()
        self.live_players.clear()
        self.invalidated_tokens.clear()
        self._seed_data()

    # ==================== USER OPERATIONS ====================

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID."""
        record = self.users.get(user_id)
        if not record:
            return None
        return User(
            id=record["id"],
            username=record["username"],
            email=record["email"],
            highScore=record["high_score"],
            gamesPlayed=record["games_played"],
            createdAt=record["created_at"],
        )

    def get_user_by_email(self, email: str) -> UserRecord | None:
        """Get a user record by email (includes password hash)."""
        for user in self.users.values():
            if user["email"].lower() == email.lower():
                return user
        return None

    def get_user_by_username(self, username: str) -> UserRecord | None:
        """Get a user record by username."""
        for user in self.users.values():
            if user["username"].lower() == username.lower():
                return user
        return None

    def create_user(self, username: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        user_id = str(uuid4())
        now = datetime.now(UTC)
        record = UserRecord(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            high_score=0,
            games_played=0,
            created_at=now,
        )
        self.users[user_id] = record
        return User(
            id=user_id,
            username=username,
            email=email,
            highScore=0,
            gamesPlayed=0,
            createdAt=now,
        )

    def update_user(self, user_id: str, username: str | None = None) -> User | None:
        """Update a user's profile."""
        record = self.users.get(user_id)
        if not record:
            return None
        if username:
            record["username"] = username
            # Update username in leaderboard entries
            for entry in self.leaderboard.values():
                if entry["user_id"] == user_id:
                    entry["username"] = username
        return User(
            id=record["id"],
            username=record["username"],
            email=record["email"],
            highScore=record["high_score"],
            gamesPlayed=record["games_played"],
            createdAt=record["created_at"],
        )

    def update_user_stats(self, user_id: str, score: int) -> None:
        """Update user stats after a game."""
        record = self.users.get(user_id)
        if record:
            record["games_played"] += 1
            if score > record["high_score"]:
                record["high_score"] = score

    # ==================== LEADERBOARD OPERATIONS ====================

    def get_leaderboard(
        self, limit: int = 10, mode: GameMode | None = None
    ) -> list[LeaderboardEntry]:
        """Get the leaderboard entries."""
        entries = list(self.leaderboard.values())
        if mode:
            entries = [e for e in entries if e["mode"] == mode.value]
        entries.sort(key=lambda x: x["score"], reverse=True)
        entries = entries[:limit]
        return [
            LeaderboardEntry(
                id=e["id"],
                username=e["username"],
                score=e["score"],
                mode=GameMode(e["mode"]),
                date=e["date"],
            )
            for e in entries
        ]

    def add_score(self, user_id: str, username: str, score: int, mode: GameMode) -> LeaderboardEntry:
        """Add a score to the leaderboard."""
        entry_id = str(uuid4())
        now = datetime.now(UTC)
        record = LeaderboardRecord(
            id=entry_id,
            user_id=user_id,
            username=username,
            score=score,
            mode=mode.value,
            date=now,
        )
        self.leaderboard[entry_id] = record
        self.update_user_stats(user_id, score)
        return LeaderboardEntry(
            id=entry_id,
            username=username,
            score=score,
            mode=mode,
            date=now,
        )

    def get_user_rank(self, user_id: str) -> int | None:
        """Get a user's rank in the leaderboard."""
        user = self.users.get(user_id)
        if not user:
            return None
        # Get unique users sorted by high score
        user_scores = {}
        for entry in self.leaderboard.values():
            uid = entry["user_id"]
            if uid not in user_scores or entry["score"] > user_scores[uid]:
                user_scores[uid] = entry["score"]
        # Sort by score descending
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (uid, _) in enumerate(sorted_users, 1):
            if uid == user_id:
                return rank
        # User has no scores, rank them last
        return len(sorted_users) + 1

    # ==================== LIVE PLAYER OPERATIONS ====================

    def get_live_players(self) -> list[LivePlayer]:
        """Get all live players."""
        return [
            LivePlayer(
                id=p["id"],
                username=p["username"],
                score=p["score"],
                mode=GameMode(p["mode"]),
                snake=[Position(**pos) for pos in p["snake"]],
                food=Position(**p["food"]),
                direction=Direction(p["direction"]),
                isAlive=p["is_alive"],
                watcherCount=p["watcher_count"],
            )
            for p in self.live_players.values()
        ]

    def get_live_player(self, player_id: str) -> LivePlayer | None:
        """Get a specific live player."""
        p = self.live_players.get(player_id)
        if not p:
            return None
        return LivePlayer(
            id=p["id"],
            username=p["username"],
            score=p["score"],
            mode=GameMode(p["mode"]),
            snake=[Position(**pos) for pos in p["snake"]],
            food=Position(**p["food"]),
            direction=Direction(p["direction"]),
            isAlive=p["is_alive"],
            watcherCount=p["watcher_count"],
        )

    def join_watcher(self, player_id: str) -> int | None:
        """Add a watcher to a live player. Returns new watcher count or None if not found."""
        player = self.live_players.get(player_id)
        if not player:
            return None
        player["watcher_count"] += 1
        return player["watcher_count"]

    def leave_watcher(self, player_id: str) -> int | None:
        """Remove a watcher from a live player. Returns new watcher count or None if not found."""
        player = self.live_players.get(player_id)
        if not player:
            return None
        player["watcher_count"] = max(0, player["watcher_count"] - 1)
        return player["watcher_count"]

    # ==================== TOKEN OPERATIONS ====================

    def invalidate_token(self, token: str) -> None:
        """Add a token to the invalidated set."""
        self.invalidated_tokens.add(token)

    def is_token_valid(self, token: str) -> bool:
        """Check if a token is still valid (not invalidated)."""
        return token not in self.invalidated_tokens


# Global database instance
db = MockDatabase()
