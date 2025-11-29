"""Dependencies for API endpoints."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token
from app.services.database_service import DatabaseService

# HTTP Bearer token scheme
security = HTTPBearer()


def get_db_service(db: Session = Depends(get_db)) -> DatabaseService:
    """Get database service instance."""
    return DatabaseService(db)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db_service: Annotated[DatabaseService, Depends(get_db_service)],
) -> User:
    """Get the current authenticated user from the JWT token."""
    token = credentials.credentials

    # Check if token has been invalidated
    if not db_service.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Token has been invalidated"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode the token
    token_data = decode_access_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the user from the database
    user = db_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "USER_NOT_FOUND", "message": "User not found"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """Get the current JWT token."""
    return credentials.credentials


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentToken = Annotated[str, Depends(get_current_token)]
DatabaseServiceDep = Annotated[DatabaseService, Depends(get_db_service)]
