"""
Brute-force protection on /api/v1/auth/login:

1. per-account failed-login lockout (sliding window, settings-driven)
2. per-IP cap shared across auth endpoints

Both layers must return identical generic responses whether the submitted
account exists or not — the limiter may never become an enumeration oracle.
"""

import pytest

from app.core.deps import login_failures, rate_limiter
from app.utils.config import settings

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"

PASSWORD = "Password123!"
WRONG = "WrongPass123!"


@pytest.fixture(autouse=True)
def fast_bcrypt():
    """Lower bcrypt cost for these tests only (register/verify dominate runtime)."""
    original = settings.bcrypt_rounds
    settings.bcrypt_rounds = 4
    yield
    settings.bcrypt_rounds = original


async def _register(client, email, username="user"):
    r = await client.post(
        REGISTER, json={"email": email, "username": username, "password": PASSWORD}
    )
    assert r.status_code == 201, r.text
    return r


async def _login(client, email, password):
    return await client.post(LOGIN, json={"email": email, "password": password})


async def _lock(client, email):
    """Drive failures past the threshold; return the first limited response."""
    limited = None
    for _ in range(settings.login_max_failures + 1):
        r = await _login(client, email, WRONG)
        if r.status_code == 429:
            limited = r
            break
        assert r.status_code == 401, r.text
    assert limited is not None, "expected lockout after exceeding failure limit"
    return limited


async def test_repeated_failed_logins_lock_out_existing_account(client):
    await _register(client, "victim@test.dev")

    statuses = [
        (await _login(client, "victim@test.dev", WRONG)).status_code
        for _ in range(settings.login_max_failures)
    ]
    assert statuses == [401] * settings.login_max_failures

    locked = await _login(client, "victim@test.dev", WRONG)
    assert locked.status_code == 429
    assert locked.json()["code"] == "rate_limited"

    # The correct password is refused too while the lockout is active.
    still_locked = await _login(client, "victim@test.dev", PASSWORD)
    assert still_locked.status_code == 429


async def test_unknown_account_gets_identical_lockout_sequence(client):
    statuses = [
        (await _login(client, "ghost@test.dev", WRONG)).status_code
        for _ in range(settings.login_max_failures)
    ]
    assert statuses == [401] * settings.login_max_failures

    locked = await _login(client, "ghost@test.dev", WRONG)
    assert locked.status_code == 429
    assert locked.json()["code"] == "rate_limited"


async def test_lockout_bodies_identical_for_existing_and_unknown_accounts(client):
    """No oracle: after the same number of failures, both return byte-equal errors."""
    await _register(client, "real@test.dev")

    real_locked = await _lock(client, "real@test.dev")
    fake_locked = await _lock(client, "never-registered@test.dev")

    assert real_locked.status_code == fake_locked.status_code == 429
    assert real_locked.json() == fake_locked.json()


async def test_failure_401_bodies_identical_for_wrong_password_and_unknown_email(client):
    await _register(client, "known@test.dev")

    wrong_pw = await _login(client, "known@test.dev", WRONG)
    unknown = await _login(client, "nobody@test.dev", PASSWORD)

    assert wrong_pw.status_code == unknown.status_code == 401
    assert wrong_pw.json() == unknown.json()


async def test_normal_successful_logins_unaffected(client):
    """A legitimate user can log in repeatedly while failures stay below the cap."""
    await _register(client, "regular@test.dev")

    for _ in range(3):
        ok = await _login(client, "regular@test.dev", PASSWORD)
        assert ok.status_code == 200
        assert ok.json()["access_token"]

    # A few sub-threshold failures don't block the next correct login…
    for _ in range(settings.login_max_failures - 1):
        assert (await _login(client, "regular@test.dev", WRONG)).status_code == 401
    ok = await _login(client, "regular@test.dev", PASSWORD)
    assert ok.status_code == 200

    # …and success RESETS the counter: a fresh full set of failures is allowed.
    for _ in range(settings.login_max_failures):
        assert (await _login(client, "regular@test.dev", WRONG)).status_code == 401
    assert (await _login(client, "regular@test.dev", WRONG)).status_code == 429


async def test_per_ip_auth_limit_returns_generic_429(client):
    """The shared per-IP auth cap is configurable and still enforced."""
    original = settings.auth_rate_limit_requests
    settings.auth_rate_limit_requests = 3
    try:
        statuses = [
            (await _login(client, "ip-limit@test.dev", WRONG)).status_code
            for _ in range(3)
        ]
        assert statuses == [401] * 3  # under the limit: plain auth failures

        blocked = await _login(client, "ip-limit@test.dev", WRONG)
        assert blocked.status_code == 429
        assert blocked.json()["code"] == "rate_limited"
        # Same generic body shape as the per-account lockout — no hint of
        # which limiter tripped or whether the account exists.
        assert set(blocked.json().keys()) == {"success", "error", "code"}
        assert blocked.json()["success"] is False
    finally:
        settings.auth_rate_limit_requests = original


async def test_lockout_expires_after_window(client, monkeypatch):
    """Failures age out: once the window passes, login is allowed again."""
    await _register(client, "expiring@test.dev")
    await _lock(client, "expiring@test.dev")
    assert (await _login(client, "expiring@test.dev", WRONG)).status_code == 429

    # Age every recorded failure past the window without sleeping in real time.
    import time as _time

    for window in login_failures._failures.values():
        for i, _ in enumerate(list(window)):
            window[i] = _time.monotonic() - settings.login_failure_window_seconds - 1

    allowed = await _login(client, "expiring@test.dev", WRONG)
    assert allowed.status_code == 401  # lockout expired; back to counting


async def test_limiters_reset_between_tests(client):
    """Autouse fixture guarantees a clean slate (guards the suite itself)."""
    assert login_failures._failures == {}
    assert rate_limiter._hits == {}
    assert (await _login(client, "clean@test.dev", WRONG)).status_code == 401
