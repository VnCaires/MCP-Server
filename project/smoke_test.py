"""Simple smoke test for the local SQLite persistence layer."""

from pathlib import Path
import sys
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project.database import get_database
from project.models import UserCreate


def main() -> None:
    """Initialize the database, create a user, and read it back."""
    database = get_database()
    database.initialize()
    unique_email = f"smoke-test-{uuid4().hex[:8]}@example.com"

    user = database.create_user(
        UserCreate(
            name="Smoke Test User",
            email=unique_email,
            description="Usuario criado para validar a persistencia local.",
        )
    )
    loaded_user = database.get_user_by_id(user.id)

    print("created_user_id:", user.id)
    print("created_user_email:", user.email)
    print("loaded_user:", loaded_user.model_dump() if loaded_user else None)


if __name__ == "__main__":
    main()
