"""Authentication router."""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentToken, CurrentUser, DatabaseServiceDep
from app.models.auth import AuthResponse, LoginRequest, LogoutResponse, SignupRequest
from app.models.user import ErrorResponse, User
from app.services.auth import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requête invalide"},
        401: {"model": ErrorResponse, "description": "Identifiants invalides"},
    },
)
async def login(
    request: LoginRequest, db_service: DatabaseServiceDep
) -> AuthResponse:
    """Authenticate a user with email and password."""
    # Find user by email
    user_record = db_service.get_user_by_email(request.email)
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )

    # Verify password
    if not verify_password(request.password, user_record["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )

    # Create access token
    token = create_access_token(user_record["id"])

    # Get user model
    user = db_service.get_user_by_id(user_record["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "SERVER_ERROR", "message": "Failed to retrieve user"},
        )

    return AuthResponse(user=user, token=token)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Requête invalide"},
        409: {"model": ErrorResponse, "description": "Email ou nom d'utilisateur déjà existant"},
    },
)
async def signup(
    request: SignupRequest, db_service: DatabaseServiceDep
) -> AuthResponse:
    """Create a new user account."""
    # Check if email already exists
    if db_service.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "EMAIL_EXISTS", "message": "Email already in use"},
        )

    # Check if username already exists
    if db_service.get_user_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "USERNAME_EXISTS", "message": "Username already taken"},
        )

    # Hash password and create user
    password_hash = get_password_hash(request.password)
    user = db_service.create_user(request.username, request.email, password_hash)

    # Create access token
    token = create_access_token(user.id)

    return AuthResponse(user=user, token=token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Non authentifié"},
    },
)
async def logout(current_user: CurrentUser, token: CurrentToken, db_service: DatabaseServiceDep) -> LogoutResponse:
    """Log out the current user and invalidate the token."""
    # Invalidate the token
    db_service.invalidate_token(token, current_user.id)
    return LogoutResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=User,
    responses={
        401: {"model": ErrorResponse, "description": "Token invalide ou expiré"},
    },
)
async def get_current_user_info(current_user: CurrentUser) -> User:
    """Get the current authenticated user's information."""
    return current_user
