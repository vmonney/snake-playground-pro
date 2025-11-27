"""Pydantic models for the Snake Playground Pro API."""

from app.models.auth import (
    AuthResponse,
    LoginRequest,
    LogoutResponse,
    SignupRequest,
    TokenData,
)
from app.models.leaderboard import (
    LeaderboardEntry,
    SubmitScoreRequest,
    UserRankResponse,
)
from app.models.live import (
    Direction,
    GameStateData,
    LivePlayer,
    Position,
    WatcherCountResponse,
    WebSocketGameStateMessage,
)
from app.models.user import ErrorResponse, GameMode, UpdateProfileRequest, User, UserStats

__all__ = [
    # Auth
    "LoginRequest",
    "SignupRequest",
    "AuthResponse",
    "LogoutResponse",
    "TokenData",
    # User
    "User",
    "UserStats",
    "UpdateProfileRequest",
    "ErrorResponse",
    "GameMode",
    # Leaderboard
    "LeaderboardEntry",
    "SubmitScoreRequest",
    "UserRankResponse",
    # Live
    "Position",
    "Direction",
    "LivePlayer",
    "WatcherCountResponse",
    "WebSocketGameStateMessage",
    "GameStateData",
]
