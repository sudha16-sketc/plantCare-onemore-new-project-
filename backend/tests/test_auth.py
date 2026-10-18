"""Authentication flow tests."""

import pytest


async def test_register_and_me(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.dev", "username": "newbie", "password": "Password123!"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == "new@test.dev"
    assert "password" not in r.text

    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["username"] == "newbie"


async def test_register_duplicate_email(client):
    payload = {"email": "dup@test.dev", "username": "one", "password": "Password123!"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    r = await client.post("/api/v1/auth/register", json={**payload, "username": "two"})
    assert r.status_code == 409
    assert r.json()["code"] == "email_taken"


async def test_register_weak_password(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.dev", "username": "weak", "password": "short"},
    )
    assert r.status_code == 422


async def test_login_success_and_failure(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.dev", "username": "loginuser", "password": "Password123!"},
    )
    ok = await client.post(
        "/api/v1/auth/login", json={"email": "login@test.dev", "password": "Password123!"}
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = await client.post(
        "/api/v1/auth/login", json={"email": "login@test.dev", "password": "WrongPass123!"}
    )
    assert bad.status_code == 401

    unknown = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@test.dev", "password": "Password123!"}
    )
    # Same error shape as wrong password — no user enumeration.
    assert unknown.status_code == 401
    assert unknown.json()["error"] == bad.json()["error"]


async def test_me_requires_token(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401


async def test_me_rejects_garbage_token(client):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


async def test_me_rejects_expired_token(client, store):
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.utils.config import settings

    user = await store.create_user("exp@test.dev", "expuser", hash_pw())
    token = jwt.encode(
        {
            "sub": user.id,
            "iat": int(datetime.now(timezone.utc).timestamp()) - 3600,
            "exp": int(datetime.now(timezone.utc).timestamp()) - 60,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def hash_pw():
    from app.core.security import hash_password

    return hash_password("Password123!")


async def test_update_profile(client, auth_headers):
    headers, _ = auth_headers
    r = await client.patch(
        "/api/v1/auth/me", json={"username": "renamed"}, headers=headers
    )
    assert r.status_code == 200
    assert r.json()["username"] == "renamed"
