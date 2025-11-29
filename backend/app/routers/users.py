"""Users router."""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DatabaseServiceDep
from app.models.user import ErrorResponse, UpdateProfileRequest, User, UserStats

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
    response_model=User,
    responses={
        404: {"model": ErrorResponse, "description": "Utilisateur non trouvé"},
    },
)
async def get_user_profile(user_id: str, db_service: DatabaseServiceDep) -> User:
    """Get a user's public profile by ID."""
    user = db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=User,
    responses={
        401: {"model": ErrorResponse, "description": "Non authentifié"},
        403: {"model": ErrorResponse, "description": "Non autorisé à modifier ce profil"},
        404: {"model": ErrorResponse, "description": "Utilisateur non trouvé"},
    },
)
async def update_user_profile(
    user_id: str,
    request: UpdateProfileRequest,
    current_user: CurrentUser,
    db_service: DatabaseServiceDep,
) -> User:
    """Update a user's profile (username only)."""
    # Check if user exists
    existing_user = db_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
        )

    # Check if user is authorized to update this profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "FORBIDDEN", "message": "Not authorized to update this profile"},
        )

    # Check if new username is already taken by another user
    if request.username:
        existing_username_user = db_service.get_user_by_username(request.username)
        if existing_username_user and existing_username_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "USERNAME_EXISTS", "message": "Username already taken"},
            )

    # Update user
    updated_user = db_service.update_user(user_id, username=request.username)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
        )

    return updated_user


@router.get(
    "/{user_id}/stats",
    response_model=UserStats,
    responses={
        404: {"model": ErrorResponse, "description": "Utilisateur non trouvé"},
    },
)
async def get_user_stats(user_id: str, db_service: DatabaseServiceDep) -> UserStats:
    """Get a user's game statistics."""
    user = db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
        )

    rank = db_service.get_user_rank(user_id)
    if rank is None:
        rank = 1  # Default rank for new users with no scores

    return UserStats(
        highScore=user.high_score,
        gamesPlayed=user.games_played,
        rank=rank,
    )
