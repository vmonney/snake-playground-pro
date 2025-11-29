"""Token repository for invalidated tokens."""

import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import InvalidatedTokenModel


class TokenRepository:
    """Repository for token invalidation operations."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        """Create a hash of the token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    def invalidate(self, token: str, user_id: str) -> None:
        """Add a token to the invalidated list."""
        token_hash = self._hash_token(token)

        # Check if already invalidated
        stmt = select(InvalidatedTokenModel).where(
            InvalidatedTokenModel.token_jti == token_hash
        )
        existing = self.db.execute(stmt).scalar_one_or_none()

        if existing:
            return  # Already invalidated

        # Decode token to get expiration
        from jose import jwt

        from app.config import settings

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                expires_at = datetime.fromtimestamp(exp_timestamp, tz=UTC)
            else:
                # Token has no expiration, use a default
                expires_at = datetime.now(UTC) + timedelta(days=7)
        except Exception:
            # If we can't decode, use default expiration
            expires_at = datetime.now(UTC) + timedelta(days=7)

        # Create invalidation record
        invalidated = InvalidatedTokenModel(
            token_jti=token_hash,
            user_id=user_id,
            expires_at=expires_at,
        )

        self.db.add(invalidated)
        self.db.commit()

    def is_valid(self, token: str) -> bool:
        """Check if a token is still valid (not invalidated)."""
        token_hash = self._hash_token(token)

        stmt = select(InvalidatedTokenModel).where(
            InvalidatedTokenModel.token_jti == token_hash
        )
        invalidated = self.db.execute(stmt).scalar_one_or_none()

        return invalidated is None

    def cleanup_expired(self) -> int:
        """Remove expired invalidated tokens. Returns count of removed tokens."""
        now = datetime.now(UTC)

        # Delete expired tokens
        stmt = select(InvalidatedTokenModel).where(
            InvalidatedTokenModel.expires_at < now
        )
        expired_tokens = self.db.execute(stmt).scalars().all()

        for token in expired_tokens:
            self.db.delete(token)

        self.db.commit()
        return len(expired_tokens)
