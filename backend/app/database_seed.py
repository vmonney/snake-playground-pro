"""Database seeding for initial test data."""

from app.database import get_db_context
from app.models.db_models import LeaderboardModel, UserModel
from app.services.auth import get_password_hash
from app.services.live_player_service import live_player_service


def seed_database() -> None:
    """Seed the database with initial test data."""

    with get_db_context() as db:
        # Check if already seeded
        existing_users = db.query(UserModel).count()
        if existing_users > 0:
            print("Database already seeded, skipping...")
            return

        # Create test users
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
            db.add(user)

        db.commit()

        # Create leaderboard entries
        leaderboard_data = [
            {
                "user_id": "user-1",
                "username": "SnakeMaster",
                "score": 1500,
                "mode": "walls",
            },
            {
                "user_id": "user-2",
                "username": "PyPlayer",
                "score": 1200,
                "mode": "walls",
            },
            {
                "user_id": "user-1",
                "username": "SnakeMaster",
                "score": 1100,
                "mode": "pass-through",
            },
            {"user_id": "user-3", "username": "GamePro", "score": 800, "mode": "walls"},
        ]

        for entry_data in leaderboard_data:
            entry = LeaderboardModel(
                user_id=entry_data["user_id"],
                username=entry_data["username"],
                score=entry_data["score"],
                mode=entry_data["mode"],
            )
            db.add(entry)

        db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()
