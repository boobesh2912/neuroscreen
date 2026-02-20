"""JWT and password hashing helpers."""

from datetime import datetime, timedelta, timezone
import hmac
import hashlib
from typing import Any
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
PBKDF2_ITERATIONS = 390000
PBKDF2_PREFIX = "pbkdf2_sha256"


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    final_salt = salt or uuid.uuid4().hex
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        final_salt.encode(),
        PBKDF2_ITERATIONS,
    ).hex()
    hashed = f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${digest}"
    return final_salt, hashed


def verify_password(plain_password: str, salt: str, password_hash: str) -> bool:
    if password_hash.startswith(f"{PBKDF2_PREFIX}$"):
        parts = password_hash.split("$", 2)
        if len(parts) != 3:
            return False
        _, iterations_raw, expected_digest = parts
        try:
            iterations = int(iterations_raw)
        except ValueError:
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode(),
            salt.encode(),
            iterations,
        ).hex()
        return hmac.compare_digest(digest, expected_digest)

    # Backward-compatible verification for legacy SHA-256 hashes.
    legacy_hash = hashlib.sha256(salt.encode() + plain_password.encode()).hexdigest()
    return hmac.compare_digest(legacy_hash, password_hash)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
    return payload
