"""Create a new Chiron user."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from models import User


def create_user(email: str):
    """Create a new user and display credentials."""
    db = SessionLocal()

    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ User with email {email} already exists!")
            print(f"   User ID: {existing.id}")
            print(f"   API Key: {existing.api_key}")
            return

        # Create new user
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

        print("✅ User created successfully!")
        print(f"\n📧 Email: {user.email}")
        print(f"🆔 User ID: {user.id}")
        print(f"🔑 API Key: {user.api_key}")
        print(f"\n💡 Save these credentials - you'll need them to access the API!")

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_user.py <email>")
        print("Example: python scripts/create_user.py craig@example.com")
        sys.exit(1)

    email = sys.argv[1]
    create_user(email)
