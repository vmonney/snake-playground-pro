"""User repository for database operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import LeaderboardModel, UserModel
from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        """Get a user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        user_model = self.db.execute(stmt).scalar_one_or_none()

        if not user_model:
            return None

        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            highScore=user_model.high_score,
            gamesPlayed=user_model.games_played,
            createdAt=user_model.created_at,
        )

    def get_by_email(self, email: str) -> UserModel | None:
        """Get a user model by email (includes password hash)."""
        stmt = select(UserModel).where(UserModel.email.ilike(email))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> UserModel | None:
        """Get a user model by username."""
        stmt = select(UserModel).where(UserModel.username.ilike(username))
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, username: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        user_model = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            high_score=0,
            games_played=0,
        )
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)

        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            highScore=user_model.high_score,
            gamesPlayed=user_model.games_played,
            createdAt=user_model.created_at,
        )

    def update(self, user_id: str, username: str | None = None) -> User | None:
        """Update a user's profile."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        user_model = self.db.execute(stmt).scalar_one_or_none()

        if not user_model:
            return None

        if username:
            user_model.username = username

            # Update denormalized username in leaderboard entries
            leaderboard_stmt = select(LeaderboardModel).where(
                LeaderboardModel.user_id == user_id
            )
            leaderboard_entries = self.db.execute(leaderboard_stmt).scalars().all()
            for entry in leaderboard_entries:
                entry.username = username

        self.db.commit()
        self.db.refresh(user_model)

        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            highScore=user_model.high_score,
            gamesPlayed=user_model.games_played,
            createdAt=user_model.created_at,
        )

    def update_stats(self, user_id: str, score: int) -> None:
        """Update user stats after a game."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        user_model = self.db.execute(stmt).scalar_one_or_none()

        if user_model:
            user_model.games_played += 1
            if score > user_model.high_score:
                user_model.high_score = score
            self.db.commit()
