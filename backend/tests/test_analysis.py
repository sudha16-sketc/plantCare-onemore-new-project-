"""Photo analysis endpoint tests (Gemini mocked)."""

import pytest

from app.core.deps import rate_limiter
from app.utils.config import settings
from tests.conftest import PNG_1PX


@pytest.fixture(autouse=True)
def clear_rate_limits():
    rate_limiter._hits.clear()
    yield
    rate_limiter._hits.clear()


async def _upload(client, content: bytes, mime: str, filename: str = "photo"):
    return await client.post(
        "/api/v1/analyze/photo",
        files={"file": (filename, content, mime)},
    )


async def test_analyze_success(client, mock_gemini_analysis):
    r = await _upload(client, PNG_1PX, "image/png")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    a = body["analysis"]
    assert a["identification"]["likely_name"]
    assert a["identification"]["confidence"] in ("low", "medium", "high")
    assert a["disclaimer"]  # always present
    assert body["metadata"]["image_mime_type"] == "image/png"
    assert body["metadata"]["image_bytes"] == len(PNG_1PX)


async def test_reject_unsupported_mime(client, mock_gemini_analysis):
    r = await _upload(client, b"{}", "application/json", filename="x.json")
    assert r.status_code == 415
    assert r.json()["code"] == "unsupported_media_type"


async def test_reject_magic_byte_mismatch(client, mock_gemini_analysis):
    """Content that claims image/png but is not a PNG."""
    r = await _upload(client, b"this is definitely not a png image at all, ok?", "image/png")
    assert r.status_code == 400
    assert r.json()["code"] == "image_invalid"


async def test_reject_empty_file(client, mock_gemini_analysis):
    r = await _upload(client, b"", "image/png")
    assert r.status_code == 400


async def test_reject_oversized_file(client, mock_gemini_analysis):
    settings_limit = 1024  # shrink limit for the test

    
    settings.max_upload_bytes = settings_limit
    try:
        big_png = PNG_1PX + b"\x00" * (settings_limit + 100)
        r = await _upload(client, big_png, "image/png")
        assert r.status_code == 413
        assert r.json()["code"] == "image_too_large"
    finally:
        settings.max_upload_bytes = 8 * 1024 * 1024


async def test_accepts_jpeg_magic(client, mock_gemini_analysis):
    jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 200
    r = await _upload(client, jpeg, "image/jpeg")
    assert r.status_code == 200


async def test_accepts_webp_magic(client, mock_gemini_analysis):
    webp = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 200
    r = await _upload(client, webp, "image/webp")
    assert r.status_code == 200


async def test_ai_failure_returns_safe_error(client, failing_gemini):
    r = await _upload(client, PNG_1PX, "image/png")
    assert r.status_code == 504
    body = r.json()
    assert body["code"] == "ai_timeout"
    assert "Traceback" not in r.text


async def test_rate_limit(client, mock_gemini_analysis):
    
    settings.ai_rate_limit_requests = 1
    rate_limiter._hits.clear()
    try:
        assert (await _upload(client, PNG_1PX, "image/png")).status_code == 200
        r = await _upload(client, PNG_1PX, "image/png")
        assert r.status_code == 429
    finally:
        settings.ai_rate_limit_requests = 1000
        rate_limiter._hits.clear()
