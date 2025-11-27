"""User-related Pydantic models."""

import re
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class GameMode(str, Enum):
    """Game mode enum."""

    WALLS = "walls"
    PASS_THROUGH = "pass-through"


class User(BaseModel):
    """User model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    high_score: Annotated[int, Field(ge=0, alias="highScore")] = 0
    games_played: Annotated[int, Field(ge=0, alias="gamesPlayed")] = 0
    created_at: Annotated[datetime, Field(alias="createdAt")]


class UserStats(BaseModel):
    """User statistics model."""

    high_score: Annotated[int, Field(ge=0, alias="highScore")]
    games_played: Annotated[int, Field(ge=0, alias="gamesPlayed")]
    rank: Annotated[int, Field(ge=1)]


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""

    username: Annotated[str | None, Field(min_length=3, max_length=30)] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only alphanumeric characters, underscores, and hyphens")
        return v


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    message: str
