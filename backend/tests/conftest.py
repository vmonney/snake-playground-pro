"""Pytest configuration and fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.services.database import db
from main import app


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    """Reset the database before each test."""
    db.reset()
    yield


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
