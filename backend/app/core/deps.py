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

    def reset(self) -> None:
        """Clear all counters (used by tests)."""
        self._hits.clear()


rate_limiter = RateLimiter()


class LoginFailureTracker:
    """
    Sliding-window failed-login counter keyed by normalized email.

    Failures are recorded for unknown emails too, so the lockout behaves
    identically for existing and non-existent accounts — this limiter can
    never be used as a user-enumeration oracle (it also always raises the
    same generic RateLimitError body as the per-IP limiter).

    Like RateLimiter, state is per-process: in multi-worker deployments
    each worker enforces its own counters.
    """

    # Distinct tracked keys before a whole-dict sweep (bounds memory under
    # attacks that submit millions of unique emails).
    _max_keys = 50_000

    def __init__(self) -> None:
        self._failures: Dict[str, Deque[float]] = defaultdict(deque)

    def _prune(self, key: str, now: float, window_seconds: int) -> None:
        window = self._failures.get(key)
        if not window:
            return
        while window and now - window[0] > window_seconds:
            window.popleft()
        if not window:
            self._failures.pop(key, None)

    def check(self, email_key: str) -> None:
        """Raise RateLimitError when this key has too many recent failures."""
        now = time.monotonic()
        window_seconds = settings.login_failure_window_seconds
        self._prune(email_key, now, window_seconds)
        window = self._failures.get(email_key)
        if window is not None and len(window) >= settings.login_max_failures:
            raise RateLimitError()
        if len(self._failures) > self._max_keys:
            self._sweep(now, window_seconds)

    def record(self, email_key: str) -> None:
        self._failures[email_key].append(time.monotonic())

    def clear(self, email_key: str) -> None:
        """Drop the counter (called after a successful login)."""
        self._failures.pop(email_key, None)

    def reset(self) -> None:
        """Clear all counters (used by tests)."""
        self._failures.clear()

    def _sweep(self, now: float, window_seconds: int) -> None:
        stale = [
            key
            for key, window in self._failures.items()
            if not window or now - window[-1] > window_seconds
        ]
        for key in stale:
            self._failures.pop(key, None)


login_failures = LoginFailureTracker()


def enforce_ai_rate_limit(request: Request) -> None:
    """Rate-limit expensive AI endpoints per client IP."""
    client = request.client.host if request.client else "unknown"
    rate_limiter.check(
        key=f"ai:{client}",
        limit=settings.ai_rate_limit_requests,
        window_seconds=settings.ai_rate_limit_window_seconds,
    )


def enforce_auth_rate_limit(request: Request) -> None:
    """
    Per-IP cap across auth endpoints to slow credential stuffing.

    Counters are shared between /register and /login; the generic
    RateLimitError response does not reveal which condition tripped.
    """
    client = request.client.host if request.client else "unknown"
    rate_limiter.check(
        key=f"auth:{client}",
        limit=settings.auth_rate_limit_requests,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )


def require_local_or_debug() -> None:
    """Guard for dev-only helpers."""
    if not settings.debug:
        raise ForbiddenError("This operation is only available in debug mode.")
