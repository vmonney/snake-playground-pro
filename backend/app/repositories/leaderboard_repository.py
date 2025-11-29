"""Leaderboard repository for database operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.db_models import LeaderboardModel, UserModel
from app.models.leaderboard import LeaderboardEntry
from app.models.user import GameMode


class LeaderboardRepository:
    """Repository for leaderboard database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_leaderboard(
        self, limit: int = 10, mode: GameMode | None = None
    ) -> list[LeaderboardEntry]:
        """Get the leaderboard entries."""
        stmt = select(LeaderboardModel)

        if mode:
            stmt = stmt.where(LeaderboardModel.mode == mode.value)

        stmt = stmt.order_by(LeaderboardModel.score.desc()).limit(limit)

        entries = self.db.execute(stmt).scalars().all()

        return [
            LeaderboardEntry(
                id=entry.id,
                username=entry.username,
                score=entry.score,
                mode=GameMode(entry.mode),
                date=entry.date,
            )
            for entry in entries
        ]

    def add_score(
        self, user_id: str, username: str, score: int, mode: GameMode
    ) -> LeaderboardEntry:
        """Add a score to the leaderboard."""
        entry_model = LeaderboardModel(
            user_id=user_id,
            username=username,
            score=score,
            mode=mode.value,
        )
        self.db.add(entry_model)
        self.db.commit()
        self.db.refresh(entry_model)

        return LeaderboardEntry(
            id=entry_model.id,
            username=entry_model.username,
            score=entry_model.score,
            mode=GameMode(entry_model.mode),
            date=entry_model.date,
        )

    def get_user_rank(self, user_id: str) -> int | None:
        """Get a user's rank in the leaderboard."""
        # Check if user exists
        user_stmt = select(UserModel).where(UserModel.id == user_id)
        user = self.db.execute(user_stmt).scalar_one_or_none()

        if not user:
            return None

        # Get unique users with their highest scores
        # Using a subquery to get max score per user
        subquery = (
            select(
                LeaderboardModel.user_id,
                func.max(LeaderboardModel.score).label("max_score"),
            )
            .group_by(LeaderboardModel.user_id)
            .subquery()
        )

        # Get all users ordered by their max score
        stmt = select(subquery.c.user_id, subquery.c.max_score).order_by(
            subquery.c.max_score.desc()
        )

        results = self.db.execute(stmt).all()

        # Find the rank
        for rank, (uid, _) in enumerate(results, 1):
            if uid == user_id:
                return rank

        # User has no scores, rank them last
        return len(results) + 1
