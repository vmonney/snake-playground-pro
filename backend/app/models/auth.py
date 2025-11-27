"""Authentication-related Pydantic models."""

import re
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import User


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: Annotated[str, Field(min_length=4)]


class SignupRequest(BaseModel):
    """Signup request model."""

    username: Annotated[str, Field(min_length=3, max_length=30)]
    email: EmailStr
    password: Annotated[str, Field(min_length=4)]

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only alphanumeric characters, underscores, and hyphens")
        return v


class AuthResponse(BaseModel):
    """Authentication response model."""

    user: User
    token: str


class LogoutResponse(BaseModel):
    """Logout response model."""

    message: str


class TokenData(BaseModel):
    """Token data model for JWT payload."""

    user_id: str | None = None
