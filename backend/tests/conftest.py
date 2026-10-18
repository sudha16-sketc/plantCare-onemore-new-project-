"""
Pytest configuration and shared fixtures.

Environment is forced to a safe, isolated state BEFORE the app is imported:
- No real .env secrets are used (MONGODB_URI/GEMINI_API_KEY overridden empty)
- In-memory store + JWT_SECRET test value
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MONGODB_URI"] = ""
os.environ["MONGODB_DB"] = "plantcare_test"
os.environ["GEMINI_API_KEY"] = ""
os.environ["ALLOW_MOCK_AI"] = "false"
os.environ["JWT_SECRET"] = "test-secret-not-for-production-0123456789abcdef"
os.environ["DEBUG"] = "false"
os.environ["GENERATED_DIR"] = "test_generated_files"
os.environ["AI_RATE_LIMIT_REQUESTS"] = "1000"  # high default; tests tighten when needed

import pytest
from httpx import ASGITransport, AsyncClient

# NOTE: do NOT call get_settings.cache_clear() here — the app imports the
# module-level `settings` singleton; clearing the cache would make tests
# mutate a different Settings instance than the one the routes read.

from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.memory import MemoryStore  # noqa: E402
from app.db.store import set_store  # noqa: E402
from app.schemas.analysis import (  # noqa: E402
    PhotoAnalysis,
    PlantIdentification,
    VisibleObservation,
)
from app.schemas.plant import GeminiResponse  # noqa: E402
from app.services.gemini import gemini_service  # noqa: E402

# Valid 1x1 transparent PNG, padded past the 100-byte minimum upload size
PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478dafcc0f01f0005050202b1a81b3e0000000049454e44ae426082"
) + b"\x00" * 64


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """
    Rate-limit and login-lockout counters are module-level (in-process) state
    shared by all tests in one run — reset them around every test so ordered
    suites neither trip nor inherit limits from each other.
    """
    from app.core.deps import login_failures, rate_limiter

    rate_limiter.reset()
    login_failures.reset()
    yield
    rate_limiter.reset()
    login_failures.reset()


@pytest.fixture
async def store():
    s = MemoryStore()
    set_store(s)
    yield s
    set_store(None)


@pytest.fixture
async def client(store):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def sample_guide() -> GeminiResponse:
    return GeminiResponse.model_validate(
        {
            "plant_overview": {
                "description": "A test plant.",
                "ideal_conditions": {
                    "temperature": "20C",
                    "humidity": "50%",
                    "sunlight": "6h",
                    "soil_ph": "6.5",
                },
                "benefits": ["Test benefit"],
                "difficulty_level": "Beginner",
            },
            "growth_stages": [
                {
                    "stage_name": "Seedling",
                    "duration": "2 weeks",
                    "care_instructions": "Keep moist",
                    "key_indicators": ["True leaves"],
                }
            ],
            "daily_care": {
                "morning_routine": ["Check soil"],
                "afternoon_routine": ["Rotate pot"],
                "evening_routine": ["Mist leaves"],
                "weekly_tasks": ["Fertilize"],
            },
            "common_problems": [
                {
                    "problem": "Yellow leaves",
                    "symptoms": ["Yellowing"],
                    "solution": "Check watering",
                    "prevention": "Consistent schedule",
                }
            ],
            "additional_tips": ["Use room-temperature water"],
        }
    )


@pytest.fixture
def sample_analysis() -> PhotoAnalysis:
    return PhotoAnalysis(
        identification=PlantIdentification(
            likely_name="Test Fern",
            possible_species=["Nephrolepis exaltata"],
            confidence="medium",
            confidence_reasoning="Clear leaf structure visible",
            visible_characteristics=["Fringed fronds"],
        ),
        observations=[VisibleObservation(observation="Minor browning at tips", severity="mild")],
        possible_causes=["Low humidity"],
        care_recommendations=["Increase humidity"],
        follow_up_observations=["Check soil moisture"],
        source="gemini",
    )


@pytest.fixture
def mock_gemini_guide(monkeypatch, sample_guide):
    async def _fake(plant_data):
        return sample_guide, "gemini"

    monkeypatch.setattr(gemini_service, "generate_plant_guide", _fake)


@pytest.fixture
def mock_gemini_analysis(monkeypatch, sample_analysis):
    async def _fake(image_bytes, mime_type):
        return sample_analysis

    monkeypatch.setattr(gemini_service, "analyze_photo", _fake)


@pytest.fixture
def failing_gemini(monkeypatch):
    from app.core.errors import UpstreamAIError

    async def _fail_guide(plant_data):
        raise UpstreamAIError("The AI service is temporarily unavailable.", code="ai_unavailable")

    async def _fail_analysis(image_bytes, mime_type):
        raise UpstreamAIError("The AI service timed out.", code="ai_timeout", status_code=504)

    monkeypatch.setattr(gemini_service, "generate_plant_guide", _fail_guide)
    monkeypatch.setattr(gemini_service, "analyze_photo", _fail_analysis)


@pytest.fixture
async def auth_headers(store):
    """Register a user and return (headers, user)."""
    user = await store.create_user("alice@test.dev", "alice", hash_password("Password123!"))
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}, user


@pytest.fixture
async def other_auth_headers(store):
    user = await store.create_user("bob@test.dev", "bob", hash_password("Password123!"))
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}, user
