"""
Password hashing and JWT token helpers.

- Passwords are hashed with bcrypt (never stored or logged in plaintext).
- API tokens are signed JWTs (HS256) with an expiry claim.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from app.utils.config import settings


def hash_password(password: str) -> str:
    """Hash a password with bcrypt. Raises ValueError on empty password."""
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValueError("Password must be at most 128 characters")
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time password verification against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a signed JWT for a user id."""
    if not settings.jwt_secret:
        raise RuntimeError(
            "JWT_SECRET is not configured. Set it in the environment before enabling auth."
        )
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises jwt.PyJWTError on invalid/expired tokens — callers map this to 401.
    """
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured.")
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
