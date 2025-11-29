"""Database configuration and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.db_models import Base

# Create engine based on configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=settings.DATABASE_POOL_SIZE if not settings.DATABASE_URL.startswith("sqlite") else 5,
    max_overflow=settings.DATABASE_MAX_OVERFLOW if not settings.DATABASE_URL.startswith("sqlite") else 10,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Usage in routers:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI.

    Usage:
        with get_db_context() as db:
            user = db.query(UserModel).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
