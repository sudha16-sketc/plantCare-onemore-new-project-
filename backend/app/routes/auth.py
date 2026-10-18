"""
Authentication routes.

Passwords are hashed with bcrypt server-side; the API returns a signed JWT.
There is no client-supplied identity — every authenticated request derives
the user from the verified token.
"""

from fastapi import APIRouter, Depends, Request

from app.core.deps import enforce_auth_rate_limit, get_current_user
from app.core.errors import AppError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.store import UserRecord, get_store
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserPublic

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


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
    store = get_store()
    user = await store.get_user_by_email(body.email)
    # Same error for unknown email and wrong password (no user enumeration).
    if user is None or not verify_password(body.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password.")
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
