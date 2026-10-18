"""
Shared FastAPI dependencies: authentication, rate limiting.
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import Depends, Request
from jwt import PyJWTError

from app.core.errors import ForbiddenError, RateLimitError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.store import UserRecord, get_store
from app.utils.config import settings


async def get_current_user(request: Request) -> UserRecord:
    """
    Resolve the authenticated user from the Authorization header.

    User identity ALWAYS comes from the verified token — never from a
    client-supplied query/body field.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise UnauthorizedError("Missing bearer token. Log in to access this resource.")
    token = auth[len("Bearer ") :].strip()
    try:
        payload = decode_access_token(token)
    except PyJWTError:
        raise UnauthorizedError("Invalid or expired token. Please log in again.")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload.")
    user = await get_store().get_user_by_id(user_id)
    if user is None:
        raise UnauthorizedError("Account no longer exists.")
    return user


class RateLimiter:
    """In-process sliding-window limiter (per key). Suitable for a single instance."""

    def __init__(self) -> None:
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        window = self._hits[key]
        while window and now - window[0] > window_seconds:
            window.popleft()
        if len(window) >= limit:
            raise RateLimitError()
        window.append(now)


rate_limiter = RateLimiter()


def enforce_ai_rate_limit(request: Request) -> None:
    """Rate-limit expensive AI endpoints per client IP."""
    client = request.client.host if request.client else "unknown"
    rate_limiter.check(
        key=f"ai:{client}",
        limit=settings.ai_rate_limit_requests,
        window_seconds=settings.ai_rate_limit_window_seconds,
    )


def enforce_auth_rate_limit(request: Request) -> None:
    """Stricter limit for auth endpoints to slow credential stuffing."""
    client = request.client.host if request.client else "unknown"
    rate_limiter.check(key=f"auth:{client}", limit=20, window_seconds=60)


def require_local_or_debug() -> None:
    """Guard for dev-only helpers."""
    if not settings.debug:
        raise ForbiddenError("This operation is only available in debug mode.")
