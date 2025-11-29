"""Database service layer - provides facade for repository access."""

from sqlalchemy.orm import Session

from app.models.leaderboard import LeaderboardEntry
from app.models.user import GameMode, User
from app.repositories import LeaderboardRepository, TokenRepository, UserRepository


class DatabaseService:
    """
    Database service that provides a facade for repository access.

    This allows for clean separation between routers and database operations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.leaderboard = LeaderboardRepository(db)
        self.tokens = TokenRepository(db)

    # ==================== USER OPERATIONS ====================

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID."""
        return self.users.get_by_id(user_id)

    def get_user_by_email(self, email: str):
        """Get a user record by email (includes password hash)."""
        user_model = self.users.get_by_email(email)
        if not user_model:
            return None
        # Return dict for backward compatibility with existing code
        return {
            "id": user_model.id,
            "username": user_model.username,
            "email": user_model.email,
            "password_hash": user_model.password_hash,
            "high_score": user_model.high_score,
            "games_played": user_model.games_played,
            "created_at": user_model.created_at,
        }

    def get_user_by_username(self, username: str):
        """Get a user record by username."""
        user_model = self.users.get_by_username(username)
        if not user_model:
            return None
        # Return dict for backward compatibility
        return {
            "id": user_model.id,
            "username": user_model.username,
            "email": user_model.email,
            "password_hash": user_model.password_hash,
            "high_score": user_model.high_score,
            "games_played": user_model.games_played,
            "created_at": user_model.created_at,
        }

    def create_user(self, username: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        return self.users.create(username, email, password_hash)

    def update_user(self, user_id: str, username: str | None = None) -> User | None:
        """Update a user's profile."""
        return self.users.update(user_id, username)

    def update_user_stats(self, user_id: str, score: int) -> None:
        """Update user stats after a game."""
        self.users.update_stats(user_id, score)

    # ==================== LEADERBOARD OPERATIONS ====================

    def get_leaderboard(
        self, limit: int = 10, mode: GameMode | None = None
    ) -> list[LeaderboardEntry]:
        """Get the leaderboard entries."""
        return self.leaderboard.get_leaderboard(limit, mode)

    def add_score(
        self, user_id: str, username: str, score: int, mode: GameMode
    ) -> LeaderboardEntry:
        """Add a score to the leaderboard."""
        entry = self.leaderboard.add_score(user_id, username, score, mode)
        # Also update user stats
        self.update_user_stats(user_id, score)
        return entry

    def get_user_rank(self, user_id: str) -> int | None:
        """Get a user's rank in the leaderboard."""
        return self.leaderboard.get_user_rank(user_id)

    # ==================== TOKEN OPERATIONS ====================

    def invalidate_token(self, token: str, user_id: str) -> None:
        """Add a token to the invalidated set."""
        self.tokens.invalidate(token, user_id)

    def is_token_valid(self, token: str) -> bool:
        """Check if a token is still valid (not invalidated)."""
        return self.tokens.is_valid(token)
