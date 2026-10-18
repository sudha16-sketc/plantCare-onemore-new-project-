"""Health and readiness endpoint tests."""

from app.utils.config import settings


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["version"]


async def test_ready_memory_mode(client):
    r = await client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["ready"] is True
    assert body["storage_mode"] == "memory"  # honest reporting, not mongodb
    assert body["storage_ok"] is True
    assert body["ai_configured"] is False  # no key in test env
    assert body["mock_ai_allowed"] is False


async def test_ready_reports_mock_ai_when_enabled(client):
    
    settings.allow_mock_ai = True
    try:
        r = await client.get("/ready")
        assert r.json()["mock_ai_allowed"] is True
    finally:
        settings.allow_mock_ai = False


async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert r.json()["documentation"] == "/docs"
