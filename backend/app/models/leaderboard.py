"""Leaderboard-related Pydantic models."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import GameMode


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    score: Annotated[int, Field(ge=0)]
    mode: GameMode
    date: datetime


class SubmitScoreRequest(BaseModel):
    """Request model for submitting a score."""

    score: Annotated[int, Field(ge=0)]
    mode: GameMode


class UserRankResponse(BaseModel):
    """Response model for user rank."""

    user_id: Annotated[str, Field(alias="userId")]
    rank: int
