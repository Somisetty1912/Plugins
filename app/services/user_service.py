from datetime import datetime
from typing import Optional
import hashlib


class UserService:
    """Service layer for user management - pure Python, no FastAPI dependencies."""

    def __init__(self):
        """Initialize the user service with an in-memory store."""
        self.users: dict = {}
        self.next_id: int = 1

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _user_exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email already exists."""
        return any(user["email"].lower() == email.lower() for user in self.users.values())

    def _user_exists_by_username(self, username: str) -> bool:
        """Check if a user with the given username already exists."""
        return any(user["username"].lower() == username.lower() for user in self.users.values())

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> dict:
        """
        Register a new user.

        Args:
            email: User's email address
            username: Username
            password: Password (will be hashed)
            full_name: Optional full name

        Returns:
            Dictionary containing the created user data

        Raises:
            ValueError: If email or username already exists
            ValueError: If email format is invalid
        """
        # Validate email is not already registered
        if self._user_exists_by_email(email):
            raise ValueError(f"Email '{email}' is already registered")

        # Validate username is not already taken
        if self._user_exists_by_username(username):
            raise ValueError(f"Username '{username}' is already taken")

        # Create the user record
        user_id = self.next_id
        self.next_id += 1

        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "password_hash": self._hash_password(password),
            "full_name": full_name,
            "created_at": datetime.utcnow()
        }

        self.users[user_id] = user

        # Return user data without password hash
        return {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "created_at": user["created_at"]
        }

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get a user by ID."""
        user = self.users.get(user_id)
        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "created_at": user["created_at"]
            }
        return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email."""
        for user in self.users.values():
            if user["email"].lower() == email.lower():
                return {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "created_at": user["created_at"]
                }
        return None

    def verify_password(self, email: str, password: str) -> bool:
        """Verify a user's password."""
        user = self.get_user_by_email(email)
        if not user:
            return False

        stored_user = next(
            (u for u in self.users.values() if u["email"].lower() == email.lower()),
            None
        )
        if not stored_user:
            return False

        return stored_user["password_hash"] == self._hash_password(password)
