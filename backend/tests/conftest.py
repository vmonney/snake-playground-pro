"""Pytest configuration and fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.database_seed import seed_database
from app.models.db_models import Base
from app.services.live_player_service import live_player_service
from main import app


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a fresh SQLite in-memory database for each test.
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
async def reset_database(test_db: Session) -> Generator[None, None, None]:
    """Reset the database and live player service before each test."""
    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Seed the database with test data
    from app.models.db_models import LeaderboardModel, UserModel
    from app.services.auth import get_password_hash

    users_data = [
        {
            "id": "user-1",
            "username": "SnakeMaster",
            "email": "snake@test.com",
            "password": "password123",
            "high_score": 1500,
            "games_played": 42,
        },
        {
            "id": "user-2",
            "username": "PyPlayer",
            "email": "python@test.com",
            "password": "password123",
            "high_score": 1200,
            "games_played": 30,
        },
        {
            "id": "user-3",
            "username": "GamePro",
            "email": "pro@test.com",
            "password": "password123",
            "high_score": 800,
            "games_played": 15,
        },
    ]

    for user_data in users_data:
        user = UserModel(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            high_score=user_data["high_score"],
            games_played=user_data["games_played"],
        )
        test_db.add(user)

    test_db.commit()

    leaderboard_data = [
        {"user_id": "user-1", "username": "SnakeMaster", "score": 1500, "mode": "walls"},
        {"user_id": "user-2", "username": "PyPlayer", "score": 1200, "mode": "walls"},
        {"user_id": "user-1", "username": "SnakeMaster", "score": 1100, "mode": "pass-through"},
        {"user_id": "user-3", "username": "GamePro", "score": 800, "mode": "walls"},
    ]

    for entry_data in leaderboard_data:
        entry = LeaderboardModel(
            user_id=entry_data["user_id"],
            username=entry_data["username"],
            score=entry_data["score"],
            mode=entry_data["mode"],
        )
        test_db.add(entry)

    test_db.commit()

    # Add a live player for testing
    await live_player_service.add_player(
        player_id="live-1",
        user_id="user-2",
        username="PyPlayer",
        mode="walls",
    )
    # Update the player state to match expected test data
    await live_player_service.update_game_state(
        player_id="live-1",
        snake=[{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}],
        food={"x": 15, "y": 12},
        direction="RIGHT",
        score=340,
        is_alive=True,
    )

    yield

    # Clear live players after test
    live_player_service._players.clear()

    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for a logged-in user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "snake@test.com", "password": "password123"},
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user2_auth_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for a second user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "python@test.com", "password": "password123"},
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def new_user_auth_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for a newly created user."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "NewPlayer",
            "email": "newplayer@test.com",
            "password": "password123",
        },
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
