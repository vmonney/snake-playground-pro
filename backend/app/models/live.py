"""Live players-related Pydantic models."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import GameMode


class Direction(str, Enum):
    """Snake direction enum."""

    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Position(BaseModel):
    """Position on the game grid."""

    x: Annotated[int, Field(ge=0)]
    y: Annotated[int, Field(ge=0)]


class LivePlayer(BaseModel):
    """Live player model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    score: Annotated[int, Field(ge=0)]
    mode: GameMode
    snake: list[Position]
    food: Position
    direction: Direction
    is_alive: Annotated[bool, Field(alias="isAlive")]
    watcher_count: Annotated[int, Field(ge=0, alias="watcherCount")]


class WatcherCountResponse(BaseModel):
    """Response model for watcher count."""

    watcher_count: Annotated[int, Field(alias="watcherCount")]


class GameStateData(BaseModel):
    """Game state data for WebSocket messages."""

    snake: list[Position]
    food: Position
    direction: Direction
    score: int
    is_alive: Annotated[bool, Field(alias="isAlive")]


class WebSocketGameStateMessage(BaseModel):
    """WebSocket message for game state updates."""

    type: Literal["gameState", "gameOver"]
    data: GameStateData
