"""Health and readiness endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.store import get_store
from app.services.gemini import gemini_service
from app.utils.config import settings

router = APIRouter(tags=["System"])


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    ready: bool
    storage_mode: str
    storage_ok: bool
    ai_configured: bool
    mock_ai_allowed: bool
    version: str


VERSION = "1.1.0"


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Cheap liveness probe: the process is up and serving requests."""
    return HealthResponse(status="healthy", version=VERSION)


@router.get("/ready", response_model=ReadyResponse, summary="Readiness probe")
async def ready() -> ReadyResponse:
    """
    Readiness probe with honest subsystem status.

    storage_mode is "mongodb" or "memory" — never claims persistence that is
    not configured. ai_configured reflects whether a Gemini key is present.
    """
    store = get_store()
    storage_ok = await store.ping()
    return ReadyResponse(
        ready=storage_ok,
        storage_mode=store.mode,
        storage_ok=storage_ok,
        ai_configured=gemini_service.configured,
        mock_ai_allowed=settings.allow_mock_ai and not gemini_service.configured,
        version=VERSION,
    )
