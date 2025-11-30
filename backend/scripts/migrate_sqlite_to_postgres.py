"""Migrate data from SQLite to PostgreSQL."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SQLITE_URL = "sqlite:///./snake_playground.db"
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://snake_user:snake_password_dev@localhost:5432/snake_playground"
)

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL."""
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)

    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()

    try:
        tables = ['users', 'leaderboard', 'invalidated_tokens']

        for table in tables:
            print(f"Migrating table: {table}")
            result = sqlite_session.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            columns = result.keys()

            print(f"  Found {len(rows)} rows")
            if not rows:
                continue

            for row in rows:
                cols = ', '.join(columns)
                placeholders = ', '.join([f":{col}" for col in columns])
                query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                row_dict = dict(zip(columns, row))

                try:
                    postgres_session.execute(text(query), row_dict)
                except Exception as e:
                    print(f"  Error: {e}")
                    continue

            postgres_session.commit()
            print(f"  Migrated {len(rows)} rows")

        print("\nMigration completed!")
    except Exception as e:
        print(f"Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    import sys

    print("SQLite to PostgreSQL migration")
    print(f"Source: {SQLITE_URL}")
    print(f"Target: {POSTGRES_URL}\n")

    # Check for --force flag
    if '--force' in sys.argv:
        migrate_data()
    else:
        response = input("Continue? (yes/no): ")
        if response.lower() == 'yes':
            migrate_data()
        else:
            print("Migration cancelled.")
