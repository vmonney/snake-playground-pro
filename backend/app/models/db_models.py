"""SQLAlchemy database models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    username: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    high_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    leaderboard_entries: Mapped[list["LeaderboardModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    invalidated_tokens: Mapped[list["InvalidatedTokenModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class LeaderboardModel(Base):
    """Leaderboard entry database model."""

    __tablename__ = "leaderboard"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # Denormalized for performance
    score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # "walls" or "pass-through"
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="leaderboard_entries")


class InvalidatedTokenModel(Base):
    """Invalidated JWT tokens (for logout functionality)."""

    __tablename__ = "invalidated_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_jti: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    invalidated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="invalidated_tokens")
