"""Background tasks for database cleanup."""

import logging
from datetime import UTC, datetime

from app.database import get_db_context
from app.repositories.token_repository import TokenRepository

logger = logging.getLogger(__name__)


def cleanup_expired_tokens() -> None:
    """Remove expired invalidated tokens from the database."""
    with get_db_context() as db:
        repo = TokenRepository(db)
        count = repo.cleanup_expired()
        logger.info(f"Cleaned up {count} expired tokens at {datetime.now(UTC)}")
        print(f"Cleaned up {count} expired tokens")


if __name__ == "__main__":
    # Can be run as a cron job or scheduled task
    cleanup_expired_tokens()
