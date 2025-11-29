
"""Database inspection utility."""

from sqlalchemy import inspect, text

from app.database import get_db_context
from app.models.db_models import Base, InvalidatedTokenModel, LeaderboardModel, UserModel


def inspect_database():
    """Inspect and display database statistics."""
    with get_db_context() as db:
        print("=" * 60)
        print("DATABASE INSPECTION")
        print("=" * 60)

        # List all tables
        print("\n📋 Tables:")
        inspector = inspect(db.bind)
        for table_name in inspector.get_table_names():
            print(f"  • {table_name}")

        # Count records in each table
        print("\n📊 Record Counts:")

        user_count = db.query(UserModel).count()
        print(f"  Users: {user_count}")

        leaderboard_count = db.query(LeaderboardModel).count()
        print(f"  Leaderboard entries: {leaderboard_count}")

        token_count = db.query(InvalidatedTokenModel).count()
        print(f"  Invalidated tokens: {token_count}")

        # Show some users
        if user_count > 0:
            print("\n👥 Users:")
            users = db.query(UserModel).limit(10).all()
            for user in users:
                print(f"  • {user.username} ({user.email}) - Score: {user.high_score}, Games: {user.games_played}")

        # Show top scores
        if leaderboard_count > 0:
            print("\n🏆 Top 5 Scores:")
            top_scores = (
                db.query(LeaderboardModel)
                .order_by(LeaderboardModel.score.desc())
                .limit(5)
                .all()
            )
            for i, entry in enumerate(top_scores, 1):
                print(f"  {i}. {entry.username} - {entry.score} ({entry.mode})")

        # Database file size (if SQLite)
        try:
            result = db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
            size_bytes = result.scalar()
            size_kb = size_bytes / 1024
            print(f"\n💾 Database size: {size_kb:.2f} KB ({size_bytes} bytes)")
        except Exception:
            pass

        print("\n" + "=" * 60)


if __name__ == "__main__":
    inspect_database()
