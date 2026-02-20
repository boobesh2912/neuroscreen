"""Authentication service."""

from datetime import datetime
from typing import Any
import uuid

from fastapi import HTTPException, status

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import LoginResponse, UserPublic, UserRegister


class AuthService:
    def register_user(self, user: UserRegister) -> dict[str, Any]:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("SELECT id FROM users WHERE username = ?", (user.username,))
            if cur.fetchone():
                raise ValueError("Username already exists")

            cur.execute("SELECT id FROM users WHERE email = ?", (user.email,))
            if cur.fetchone():
                raise ValueError("Email already registered")

            user_id = str(uuid.uuid4())
            salt, password_hash = hash_password(user.password)

            cur.execute(
                """
                INSERT INTO users (
                    id, username, password_hash, salt, email,
                    first_name, last_name, date_of_birth, phone_number,
                    address, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user.username,
                    password_hash,
                    salt,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.dob,
                    user.phone,
                    user.address,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

        return {"success": True, "message": "Registration successful", "user_id": user_id}

    def authenticate_user(self, username: str, password: str) -> LoginResponse | None:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

            if user is None:
                return None

            user_d = dict(user)
            if not verify_password(password, user_d["salt"], user_d["password_hash"]):
                return None

            now = datetime.now().isoformat()
            # Upgrade legacy SHA-256 password hashes to PBKDF2 on successful login.
            if not str(user_d["password_hash"]).startswith("pbkdf2_sha256$"):
                new_salt, new_password_hash = hash_password(password)
                cur.execute(
                    "UPDATE users SET salt = ?, password_hash = ?, last_login = ? WHERE id = ?",
                    (new_salt, new_password_hash, now, user_d["id"]),
                )
            else:
                cur.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (now, user_d["id"]),
                )
            conn.commit()

        token_payload = {
            "sub": user_d["username"],
            "user_id": user_d["id"],
            "email": user_d["email"],
            "first_name": user_d["first_name"],
            "last_name": user_d["last_name"],
        }
        access_token = create_access_token(token_payload)

        return LoginResponse(
            token=access_token,
            user=UserPublic(
                id=user_d["id"],
                username=user_d["username"],
                email=user_d["email"],
                first_name=user_d["first_name"],
                last_name=user_d["last_name"],
                phone_number=user_d.get("phone_number"),
                date_of_birth=user_d.get("date_of_birth"),
            ),
        )

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
            return dict(user) if user else None


auth_service = AuthService()


def require_user(user: dict[str, Any] | None) -> dict[str, Any]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing or invalid",
        )
    return user
