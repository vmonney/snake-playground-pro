"""Live players router with WebSocket support."""

import asyncio
import json

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from app.models.live import LivePlayer, WatcherCountResponse
from app.models.user import ErrorResponse
from app.services.database import db

router = APIRouter(prefix="/live", tags=["Live Players"])


@router.get(
    "/players",
    response_model=list[LivePlayer],
)
async def get_live_players() -> list[LivePlayer]:
    """Get all live players currently playing."""
    return db.get_live_players()


@router.get(
    "/players/{player_id}",
    response_model=LivePlayer,
    responses={
        404: {"model": ErrorResponse, "description": "Joueur non trouvé"},
    },
)
async def get_live_player(player_id: str) -> LivePlayer:
    """Get a specific live player's information."""
    player = db.get_live_player(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "PLAYER_NOT_FOUND", "message": "Player not found or no longer live"},
        )
    return player


@router.post(
    "/players/{player_id}/watch",
    response_model=WatcherCountResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Joueur non trouvé"},
    },
)
async def join_as_watcher(player_id: str) -> WatcherCountResponse:
    """Join as a watcher for a live player."""
    watcher_count = db.join_watcher(player_id)
    if watcher_count is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "PLAYER_NOT_FOUND", "message": "Player not found"},
        )
    return WatcherCountResponse(watcherCount=watcher_count)


@router.delete(
    "/players/{player_id}/watch",
    response_model=WatcherCountResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Joueur non trouvé"},
    },
)
async def leave_as_watcher(player_id: str) -> WatcherCountResponse:
    """Leave as a watcher for a live player."""
    watcher_count = db.leave_watcher(player_id)
    if watcher_count is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "PLAYER_NOT_FOUND", "message": "Player not found"},
        )
    return WatcherCountResponse(watcherCount=watcher_count)


@router.websocket("/players/{player_id}/stream")
async def player_stream(websocket: WebSocket, player_id: str) -> None:
    """WebSocket endpoint for streaming game state updates."""
    # Check if player exists
    player = db.get_live_player(player_id)
    if not player:
        await websocket.close(code=4004, reason="Player not found")
        return

    await websocket.accept()

    try:
        # Increment watcher count
        db.join_watcher(player_id)

        # Send initial game state
        player = db.get_live_player(player_id)
        if player:
            initial_message = {
                "type": "gameState",
                "data": {
                    "snake": [{"x": pos.x, "y": pos.y} for pos in player.snake],
                    "food": {"x": player.food.x, "y": player.food.y},
                    "direction": player.direction.value,
                    "score": player.score,
                    "isAlive": player.is_alive,
                },
            }
            await websocket.send_json(initial_message)

        # Simulate periodic updates (mock implementation)
        while True:
            await asyncio.sleep(1.0)  # Update every second

            # Get current player state
            player = db.get_live_player(player_id)
            if not player:
                # Player no longer live
                await websocket.send_json({
                    "type": "gameOver",
                    "data": {
                        "snake": [],
                        "food": {"x": 0, "y": 0},
                        "direction": "RIGHT",
                        "score": 0,
                        "isAlive": False,
                    },
                })
                break

            # Send updated game state
            message = {
                "type": "gameState",
                "data": {
                    "snake": [{"x": pos.x, "y": pos.y} for pos in player.snake],
                    "food": {"x": player.food.x, "y": player.food.y},
                    "direction": player.direction.value,
                    "score": player.score,
                    "isAlive": player.is_alive,
                },
            }
            await websocket.send_json(message)

    except WebSocketDisconnect:
        # Client disconnected
        db.leave_watcher(player_id)
    except Exception:
        # Handle any other exceptions
        db.leave_watcher(player_id)
        await websocket.close()
