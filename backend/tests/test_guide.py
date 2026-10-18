"""Guide generation endpoint tests (Gemini mocked; PPT generation is real/local)."""

import pytest

from app.core.deps import rate_limiter
from app.utils.config import settings

GUIDE_PAYLOAD = {
    "plant_name": "Tomato",
    "plant_type": "Vegetable",
    "climate": "Temperate",
    "sunlight_hours": 6,
    "soil_type": "Loamy",
    "watering_frequency": "Daily",
    "experience_level": "Beginner",
}


@pytest.fixture(autouse=True)
def clear_rate_limits():
    rate_limiter._hits.clear()
    yield
    rate_limiter._hits.clear()


async def test_generate_guide_success(client, mock_gemini_guide):
    r = await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["plant_care_guidance"]["plant_overview"]["description"]
    assert body["metadata"]["ai_source"] == "gemini"
    # PPT is generated locally and served via an absolute URL on this API
    vg = body["visual_guide"]
    assert vg["status"] == "success"
    assert vg["file_url"].startswith("http://test/api/v1/files/")
    assert vg["file_url"].endswith(".pptx")

    # The download URL must actually work
    dl = await client.get(vg["file_url"].replace("http://test", ""))
    assert dl.status_code == 200
    assert dl.content[:2] == b"PK"  # zip/pptx magic
    assert "attachment" in dl.headers["content-disposition"]


async def test_generate_guide_invalid_input(client):
    r = await client.post("/generate-plant-guide", json={"plant_name": "X"})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "validation_error"
    # Safe field-level errors, no raw payload echo
    assert "fields" in body
    for f in body["fields"]:
        assert "message" in f


async def test_generate_guide_sunlight_bounds(client):
    payload = {**GUIDE_PAYLOAD, "sunlight_hours": 25}
    r = await client.post("/generate-plant-guide", json=payload)
    assert r.status_code == 422


async def test_generate_guide_ai_failure_returns_safe_error(client, failing_gemini):
    r = await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)
    assert r.status_code == 502
    body = r.json()
    assert body["success"] is False
    assert body["code"] == "ai_unavailable"
    # No internal exception details leaked
    assert "Traceback" not in r.text
    assert "detail" not in body or "Traceback" not in str(body.get("detail", ""))


async def test_generate_guide_unconfigured_ai_returns_503(client, monkeypatch):
    """Without a key and without ALLOW_MOCK_AI, the API must NOT invent data."""
    from app.core.errors import UpstreamAIError
    from app.services.gemini import gemini_service

    async def _unconfigured(plant_data):
        raise UpstreamAIError(
            "AI guidance is not available on this server (no API key configured).",
            code="ai_not_configured",
            status_code=503,
        )

    monkeypatch.setattr(gemini_service, "generate_plant_guide", _unconfigured)
    r = await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)
    assert r.status_code == 503
    assert r.json()["code"] == "ai_not_configured"


async def test_mock_ai_labeled_when_enabled(client, monkeypatch):
    """When mock mode is on, responses must be labeled source=mock."""
    from app.services.gemini import gemini_service

    
    settings.allow_mock_ai = True
    try:
        # Use the real (unconfigured) service path with mock allowed
        r = await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)
        assert r.status_code == 200
        body = r.json()
        assert body["metadata"]["ai_source"] == "mock"
        assert "Mock guide" in body["plant_care_guidance"]["plant_overview"]["description"] or "mock" in body["plant_care_guidance"]["plant_overview"]["description"].lower()
    finally:
        settings.allow_mock_ai = False


async def test_ai_rate_limit(client, mock_gemini_guide):
    
    settings.ai_rate_limit_requests = 2
    rate_limiter._hits.clear()
    try:
        assert (await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)).status_code == 200
        assert (await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)).status_code == 200
        r = await client.post("/generate-plant-guide", json=GUIDE_PAYLOAD)
        assert r.status_code == 429
        assert r.json()["code"] == "rate_limited"
    finally:
        settings.ai_rate_limit_requests = 1000
        rate_limiter._hits.clear()
