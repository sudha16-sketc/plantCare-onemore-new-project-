"""
Photo-based plant identification and visible-symptom analysis.

POST /api/v1/analyze/photo (multipart/form-data)
- Validates MIME type and size BEFORE any AI call.
- Uses Gemini image input via the official SDK.
- Returns structured, schema-validated output that separates visible
  observations from possible causes, with an explicit confidence label.
"""

import logging
import time

from fastapi import APIRouter, File, Request, UploadFile

from app.core.deps import enforce_ai_rate_limit
from app.core.errors import AppError
from app.schemas.analysis import PhotoAnalysisResponse
from app.services.gemini import gemini_service
from app.utils.config import settings

logger = logging.getLogger("plantcare.analysis")

router = APIRouter(prefix="/api/v1/analyze", tags=["Analysis"])

_PHOTOS_DIR = "uploads"


@router.post(
    "/photo",
    response_model=PhotoAnalysisResponse,
    summary="Identify a plant and assess visible symptoms from a photo",
)
async def analyze_photo(request: Request, file: UploadFile = File(...)) -> PhotoAnalysisResponse:
    enforce_ai_rate_limit(request)
    started = time.time()

    # --- Validate content type ---
    mime = (file.content_type or "").lower()
    allowed = settings.get_allowed_image_types_list()
    if mime not in allowed:
        raise AppError(
            f"Unsupported image type '{mime or 'unknown'}'. Allowed: {', '.join(allowed)}.",
            status_code=415,
            code="unsupported_media_type",
        )

    # --- Read with a hard size cap (never trust Content-Length alone) ---
    max_bytes = settings.max_upload_bytes
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise AppError(
                f"Image is too large (limit {max_bytes // (1024 * 1024)} MB).",
                status_code=413,
                code="image_too_large",
            )
        chunks.append(chunk)
    image_bytes = b"".join(chunks)

    if len(image_bytes) < 100:
        raise AppError(
            "The uploaded file is empty or too small to be a photo.",
            status_code=400,
            code="image_invalid",
        )

    # --- Basic magic-byte check matches declared type ---
    if not _looks_like_image(image_bytes, mime):
        raise AppError(
            "The uploaded file content does not match its declared image type.",
            status_code=400,
            code="image_invalid",
        )

    logger.info("Analyzing photo (%s, %d bytes)", mime, len(image_bytes))
    analysis = await gemini_service.analyze_photo(image_bytes, mime)

    return gemini_service.analyze_response(
        analysis,
        mime_type=mime,
        image_bytes=len(image_bytes),
        seconds=time.time() - started,
    )


def _looks_like_image(data: bytes, mime: str) -> bool:
    """Cheap magic-byte validation for jpeg/png/webp."""
    if data[:3] == b"\xff\xd8\xff":  # JPEG
        return mime == "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return mime == "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return mime == "image/webp"
    return False
