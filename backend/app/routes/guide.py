"""
Plant care guide generation route (existing feature, hardened).

- AI failures surface as safe 5xx errors (no silent mock substitution).
- PPT download URL is returned both relative (API path) and absolute
  (built from the incoming request) so web and mobile clients work.
"""

import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.core.deps import enforce_ai_rate_limit
from app.core.errors import error_body, UpstreamAIError
from app.schemas.plant import PlantGuideResponse, PlantInputData, VisualGuideResponse
from app.services.gemini import gemini_service
from app.services.ppt_service import ppt_service
from app.utils.config import settings

logger = logging.getLogger("plantcare.guide")

router = APIRouter(tags=["Plant Care"])


def _absolute_url(request: Request, path: str) -> str:
    """Build an absolute URL for an API path using the incoming request's host."""
    return str(request.base_url).rstrip("/") + path


@router.post(
    "/generate-plant-guide",
    response_model=PlantGuideResponse,
    summary="Generate Plant Care Guide",
    description="Generate comprehensive plant care guidance using AI",
)
async def generate_plant_guide(plant_data: PlantInputData, request: Request):
    enforce_ai_rate_limit(request)
    start = time.time()

    logger.info("Generating plant guide for: %s", plant_data.plant_name)

    # Step 1: AI guidance (raises safe errors — never silently mocked).
    gemini_response, ai_source = await gemini_service.generate_plant_guide(plant_data)

    # Step 2: PPT visual guide. Failures here do not fail the whole request;
    # the response reports the visual guide as unavailable with a reason.
    visual = None
    try:
        ppt_result = await ppt_service.generate(gemini_response, plant_data.plant_name)
        visual = VisualGuideResponse(
            status=ppt_result["status"],
            file_url=_absolute_url(request, ppt_result["file_url"]),
            file_type=ppt_result["file_type"],
            message=ppt_result["message"],
        )
    except Exception:
        logger.exception("PPT generation failed for %s", plant_data.plant_name)
        visual = VisualGuideResponse(
            status="error",
            file_url=None,
            file_type=None,
            message="The presentation could not be generated, but your care guide is ready.",
        )

    processing_time = time.time() - start
    response = PlantGuideResponse(
        success=True,
        plant_care_guidance=gemini_response,
        visual_guide=visual,
        metadata={
            "plant_name": plant_data.plant_name,
            "plant_type": plant_data.plant_type,
            "climate": plant_data.climate,
            "sunlight_hours": plant_data.sunlight_hours,
            "soil_type": plant_data.soil_type,
            "watering_frequency": plant_data.watering_frequency,
            "experience_level": plant_data.experience_level,
            "ai_source": ai_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_time_seconds": round(processing_time, 2),
        },
    )
    logger.info("Guide generated in %.2fs for %s", processing_time, plant_data.plant_name)
    return response
