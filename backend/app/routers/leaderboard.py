"""Leaderboard router."""

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CurrentUser
from app.models.leaderboard import LeaderboardEntry, SubmitScoreRequest, UserRankResponse
from app.models.user import ErrorResponse, GameMode
from app.services.database import db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get(
    "",
    response_model=list[LeaderboardEntry],
)
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of entries to return"),
    mode: GameMode | None = Query(default=None, description="Filter by game mode"),
) -> list[LeaderboardEntry]:
    """Get the leaderboard entries."""
    return db.get_leaderboard(limit=limit, mode=mode)


@router.post(
    "/scores",
    response_model=LeaderboardEntry,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Requête invalide"},
        401: {"model": ErrorResponse, "description": "Non authentifié"},
    },
)
async def submit_score(
    request: SubmitScoreRequest,
    current_user: CurrentUser,
) -> LeaderboardEntry:
    """Submit a new score to the leaderboard."""
    entry = db.add_score(
        user_id=current_user.id,
        username=current_user.username,
        score=request.score,
        mode=request.mode,
    )
    return entry


@router.get(
    "/rank/{user_id}",
    response_model=UserRankResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Utilisateur non trouvé"},
    },
)
async def get_user_rank(user_id: str) -> UserRankResponse:
    """Get a user's rank in the leaderboard."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
        )

    rank = db.get_user_rank(user_id)
    if rank is None:
        rank = 1  # Default rank for users with no scores

    return UserRankResponse(userId=user_id, rank=rank)
