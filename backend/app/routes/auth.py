"""
Authentication routes.

Passwords are hashed with bcrypt server-side; the API returns a signed JWT.
There is no client-supplied identity — every authenticated request derives
the user from the verified token.

Brute-force protection (both layers always return the same generic error
envelopes regardless of whether the submitted account exists):
  1. per-IP cap across auth endpoints (enforce_auth_rate_limit)
  2. per-account failed-login lockout (login_failures)
"""

import secrets

from fastapi import APIRouter, Depends, Request

from app.core.deps import enforce_auth_rate_limit, get_current_user, login_failures
from app.core.errors import AppError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.store import UserRecord, get_store
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserPublic

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# Verified against when the email is unknown so the unknown-email path costs
# exactly one bcrypt check — same work and timing as the wrong-password path
# (prevents user enumeration by response timing). Built lazily with the
# configured bcrypt cost.
_dummy_password_hash: str | None = None


def _get_dummy_password_hash() -> str:
    global _dummy_password_hash
    if _dummy_password_hash is None:
        _dummy_password_hash = hash_password(secrets.token_urlsafe(32))
    return _dummy_password_hash


def _user_public(user: UserRecord) -> UserPublic:
    return UserPublic(
        id=user.id, email=user.email, username=user.username, created_at=user.created_at
    )


@router.post("/register", response_model=AuthResponse, status_code=201, summary="Create an account")
async def register(body: RegisterRequest, request: Request) -> AuthResponse:
    enforce_auth_rate_limit(request)
    store = get_store()
    try:
        user = await store.create_user(body.email, body.username, hash_password(body.password))
    except ValueError as exc:
        raise AppError(str(exc), status_code=409, code="email_taken")
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_user_public(user))


@router.post("/login", response_model=AuthResponse, summary="Sign in")
async def login(body: LoginRequest, request: Request) -> AuthResponse:
    enforce_auth_rate_limit(request)
    # Normalized exactly like the store indexes emails, and tracked even for
    # unknown accounts so lockout alone cannot reveal existence.
    email_key = body.email.strip().lower()
    login_failures.check(email_key)

    store = get_store()
    user = await store.get_user_by_email(body.email)
    if user is None:
        # Same error, same bcrypt work as the wrong-password path.
        verify_password(body.password, _get_dummy_password_hash())
        login_failures.record(email_key)
        raise UnauthorizedError("Invalid email or password.")
    if not verify_password(body.password, user.password_hash):
        login_failures.record(email_key)
        raise UnauthorizedError("Invalid email or password.")

    login_failures.clear(email_key)
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_user_public(user))


@router.get("/me", response_model=UserPublic, summary="Current user")
async def me(user: UserRecord = Depends(get_current_user)) -> UserPublic:
    return _user_public(user)


@router.patch("/me", response_model=UserPublic, summary="Update profile")
async def update_me(
    body: dict,
    user: UserRecord = Depends(get_current_user),
) -> UserPublic:
    username = body.get("username")
    email = body.get("email")
    if username is not None and not (3 <= len(str(username)) <= 50):
        raise AppError("Username must be 3-50 characters", status_code=422, code="validation_error")
    if email is not None and ("@" not in str(email) or len(str(email)) > 254):
        raise AppError("A valid email is required", status_code=422, code="validation_error")
    store = get_store()
    try:
        updated = await store.update_user(
            user.id,
            str(username) if username else None,
            str(email) if email else None,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=409, code="email_taken")
    if updated is None:
        raise UnauthorizedError("Account no longer exists.")
    return _user_public(updated)
