import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path

from app.core.config import get_settings


class AuthService:
    """File-backed account and token management."""

    def __init__(self):
        self.settings = get_settings()
        self.users_file = Path(self.settings.users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_default_user()

    def login(self, user_id: str, password: str) -> dict:
        self._validate_user_id(user_id)
        users = self._read()
        user = users.get(user_id)
        if not user or not self._verify_password(password, user):
            raise ValueError("Invalid account or password")
        if not user.get("token"):
            user["token"] = secrets.token_urlsafe(32)
        user["last_login_at"] = datetime.now().isoformat()
        users[user_id] = user
        self._write(users)
        return {
            "user_id": user_id,
            "token": user["token"],
            "users_file": str(self.users_file),
        }

    def authenticate(self, token: str = None) -> str:
        if not token:
            raise ValueError("Authentication required")
        users = self._read()
        for user_id, user in users.items():
            if secrets.compare_digest(user.get("token", ""), token):
                return user_id
        raise ValueError("Invalid authentication token")

    def verify_project_owner(self, authenticated_user: str, user_id: str) -> None:
        if authenticated_user != user_id:
            raise ValueError("You can only access your own projects")

    def _ensure_default_user(self) -> None:
        if self.users_file.exists():
            return
        salt = secrets.token_hex(16)
        users = {
            "default-user": {
                "password_hash": self._hash_password("yoko1234", salt),
                "salt": salt,
                "token": secrets.token_urlsafe(32),
                "created_at": datetime.now().isoformat(),
            }
        }
        self._write(users)

    def _read(self) -> dict:
        if not self.users_file.exists():
            self._ensure_default_user()
        with self.users_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, users: dict) -> None:
        temporary = self.users_file.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2, ensure_ascii=False)
        temporary.replace(self.users_file)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

    @classmethod
    def _verify_password(cls, password: str, user: dict) -> bool:
        return secrets.compare_digest(
            cls._hash_password(password, user["salt"]),
            user["password_hash"],
        )

    @staticmethod
    def _validate_user_id(user_id: str) -> None:
        if (
            not user_id
            or user_id in {".", ".."}
            or "/" in user_id
            or "\\" in user_id
            or Path(user_id).name != user_id
        ):
            raise ValueError("Invalid account")
