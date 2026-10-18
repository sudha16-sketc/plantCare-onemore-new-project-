"""
Gemini AI service.

Uses the official google-genai SDK (API key is configured on the client —
never placed in URLs, logs, or client responses).

Failure policy:
- Provider/timeout/quota/parse failures raise UpstreamAIError with a safe
  message. They are NEVER silently replaced with mock data.
- Mock payloads are returned only when settings.allow_mock_ai is true AND no
  API key is configured, and are labeled source="mock".
"""

import json
import logging
import re
from typing import Optional, Tuple

from app.core.errors import AppError, UpstreamAIError
from app.schemas.analysis import (
    AnalysisMetadata,
    PhotoAnalysis,
    PhotoAnalysisResponse,
    PlantIdentification,
    VisibleObservation,
)
from app.schemas.plant import GeminiResponse, PlantInputData
from app.utils.config import settings

logger = logging.getLogger("plantcare.gemini")


class GeminiService:
    """Service class for Google Gemini AI (text + image understanding)."""

    def __init__(self) -> None:
        self._client = None
        self.model = settings.gemini_model

    @property
    def configured(self) -> bool:
        return bool(settings.gemini_api_key)

    def _get_client(self):
        """Lazily construct the official SDK client."""
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    # ------------------------------------------------------------------
    # Plant care guide (text)
    # ------------------------------------------------------------------
    def _build_prompt(self, plant_data: PlantInputData) -> str:
        return f"""You are an expert botanist and plant care specialist. Based on the following plant information,
provide comprehensive care guidance in strict JSON format.

Plant Information:
- Name: {plant_data.plant_name}
- Type: {plant_data.plant_type}
- Climate: {plant_data.climate}
- Daily Sunlight: {plant_data.sunlight_hours} hours
- Soil Type: {plant_data.soil_type}
- Current Watering Frequency: {plant_data.watering_frequency}
- Gardener Experience Level: {plant_data.experience_level}

Provide a detailed plant care guide with the following structure (respond ONLY with valid JSON, no markdown):

{{
  "plant_overview": {{
    "description": "Detailed description of the plant (2-3 sentences)",
    "ideal_conditions": {{
      "temperature": "Temperature range",
      "humidity": "Humidity percentage",
      "sunlight": "Sunlight requirements",
      "soil_ph": "Ideal pH range"
    }},
    "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
    "difficulty_level": "Beginner/Intermediate/Advanced"
  }},
  "growth_stages": [
    {{
      "stage_name": "Germination/Seedling/etc.",
      "duration": "Time period",
      "care_instructions": "Specific care during this stage",
      "key_indicators": ["Indicator 1", "Indicator 2"]
    }}
  ],
  "daily_care": {{
    "morning_routine": ["Task 1", "Task 2"],
    "afternoon_routine": ["Task 1", "Task 2"],
    "evening_routine": ["Task 1", "Task 2"],
    "weekly_tasks": ["Task 1", "Task 2", "Task 3"]
  }},
  "common_problems": [
    {{
      "problem": "Problem name",
      "symptoms": ["Symptom 1", "Symptom 2"],
      "solution": "Detailed solution",
      "prevention": "Prevention tips"
    }}
  ],
  "additional_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}
Tailor the advice to the gardener's experience level: {plant_data.experience_level}.
Include at least 3-4 growth stages, 4-5 common problems, and 5-7 additional tips.
Respond with ONLY the JSON object, no additional text or markdown formatting."""

    async def generate_plant_guide(self, plant_data: PlantInputData) -> Tuple[GeminiResponse, str]:
        """
        Generate plant care guidance.

        Returns (response, source) where source is "gemini" or "mock".
        Raises UpstreamAIError on failure. Falls back to a clearly-labeled
        mock only when explicitly enabled and unconfigured.
        """
        if not self.configured:
            if settings.allow_mock_ai:
                logger.warning("Gemini not configured — returning MOCK guide (ALLOW_MOCK_AI=true)")
                return self._mock_guide(plant_data), "mock"
            raise UpstreamAIError(
                "AI guidance is not available on this server (no API key configured).",
                code="ai_not_configured",
                status_code=503,
            )

        from google.genai import errors as genai_errors

        client = self._get_client()
        prompt = self._build_prompt(plant_data)

        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except genai_errors.ClientError as exc:
            status = getattr(exc, "code", None)
            if status in (429,):
                raise UpstreamAIError(
                    "The AI service is rate-limited right now. Please try again in a minute.",
                    code="ai_rate_limited",
                    status_code=429,
                    detail=str(exc),
                )
            if status in (401, 403):
                logger.error("Gemini authentication/authorization failure (check API key)")
                raise UpstreamAIError(
                    "The AI service rejected the server credentials.",
                    code="ai_auth_error",
                    detail=str(exc),
                )
            raise UpstreamAIError(
                "The AI service returned an error for this request.",
                code="ai_provider_error",
                detail=str(exc),
            )
        except genai_errors.ServerError as exc:
            status = getattr(exc, "code", None)
            if status == 504 or "timeout" in str(exc).lower():
                raise UpstreamAIError(
                    "The AI service timed out. Please try again.",
                    code="ai_timeout",
                    status_code=504,
                    detail=str(exc),
                )
            raise UpstreamAIError(
                "The AI service is temporarily unavailable. Please try again shortly.",
                code="ai_unavailable",
                detail=str(exc),
            )
        except Exception as exc:  # network / SDK internals
            logger.exception("Unexpected Gemini client failure")
            raise UpstreamAIError(
                "Could not reach the AI service. Please try again later.",
                code="ai_unreachable",
                detail=type(exc).__name__,
            )

        text = (response.text or "").strip()
        if not text:
            raise UpstreamAIError(
                "The AI service returned an empty response.",
                code="ai_empty_response",
            )

        data = self._parse_json_object(text)
        try:
            return GeminiResponse.model_validate(data), "gemini"
        except Exception as exc:
            logger.warning("Gemini guide response failed schema validation: %s", exc)
            raise UpstreamAIError(
                "The AI service returned an unexpected response format.",
                code="ai_invalid_response",
                detail=str(exc),
            )

    # ------------------------------------------------------------------
    # Photo analysis (image understanding)
    # ------------------------------------------------------------------
    _ANALYSIS_PROMPT = """You are a careful plant-care assistant analyzing one photo.

Identify the plant if possible and describe ONLY what is visible in the image.

Rules:
- If you are not confident about the plant identity, say so explicitly (confidence: low) and explain why.
- Describe visible characteristics and any visible symptoms as OBSERVATIONS, not confirmed diagnoses.
- For possible causes, use cautious language ("may", "could") and list plausible explanations only.
- Include concrete follow-up checks the person can do (e.g. "check the underside of leaves", "feel the soil 2cm down").
- Respond with ONLY a JSON object matching this shape, no markdown:

{
  "identification": {
    "likely_name": "common name",
    "possible_species": ["species 1", "species 2"],
    "confidence": "low|medium|high",
    "confidence_reasoning": "why this confidence",
    "visible_characteristics": ["trait 1", "trait 2"]
  },
  "observations": [
    {"observation": "what is visible", "severity": "none|mild|moderate|severe|unclear"}
  ],
  "possible_causes": ["plausible cause 1", "plausible cause 2"],
  "care_recommendations": ["recommendation 1", "recommendation 2"],
  "follow_up_observations": ["check 1", "check 2"]
}"""

    async def analyze_photo(self, image_bytes: bytes, mime_type: str) -> PhotoAnalysis:
        """
        Analyze a plant photo with Gemini image input.

        Raises UpstreamAIError on provider problems; returns labeled mock only
        when allow_mock_ai is true and no key is configured.
        """
        if not self.configured:
            if settings.allow_mock_ai:
                logger.warning("Gemini not configured — returning MOCK analysis (ALLOW_MOCK_AI=true)")
                return self._mock_analysis()
            raise UpstreamAIError(
                "AI photo analysis is not available on this server (no API key configured).",
                code="ai_not_configured",
                status_code=503,
            )

        from google import genai
        from google.genai import errors as genai_errors

        client = self._get_client()
        contents = [
            types_part_bytes(image_bytes, mime_type),
            self._ANALYSIS_PROMPT,
        ]

        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=contents,
            )
        except genai_errors.ClientError as exc:
            status = getattr(exc, "code", None)
            if status == 429:
                raise UpstreamAIError(
                    "The AI service is rate-limited right now. Please try again in a minute.",
                    code="ai_rate_limited",
                    status_code=429,
                    detail=str(exc),
                )
            if status in (401, 403):
                raise UpstreamAIError(
                    "The AI service rejected the server credentials.",
                    code="ai_auth_error",
                    detail=str(exc),
                )
            if status == 400 and "image" in str(exc).lower():
                raise AppError(
                    "The image could not be processed by the AI service.",
                    status_code=400,
                    code="image_unusable",
                    detail=str(exc),
                )
            raise UpstreamAIError(
                "The AI service returned an error for this image.",
                code="ai_provider_error",
                detail=str(exc),
            )
        except genai_errors.ServerError as exc:
            status = getattr(exc, "code", None)
            if status == 504 or "timeout" in str(exc).lower():
                raise UpstreamAIError(
                    "The AI service timed out while analyzing the image.",
                    code="ai_timeout",
                    status_code=504,
                    detail=str(exc),
                )
            raise UpstreamAIError(
                "The AI service is temporarily unavailable. Please try again shortly.",
                code="ai_unavailable",
                detail=str(exc),
            )
        except Exception as exc:
            logger.exception("Unexpected Gemini image client failure")
            raise UpstreamAIError(
                "Could not reach the AI service. Please try again later.",
                code="ai_unreachable",
                detail=type(exc).__name__,
            )

        text = (response.text or "").strip()
        if not text:
            raise UpstreamAIError(
                "The AI service returned an empty analysis.",
                code="ai_empty_response",
            )

        data = self._parse_json_object(text)
        try:
            return PhotoAnalysis.model_validate(data)
        except Exception as exc:
            logger.warning("Gemini analysis response failed schema validation: %s", exc)
            raise UpstreamAIError(
                "The AI service returned an unexpected analysis format.",
                code="ai_invalid_response",
                detail=str(exc),
            )

    def analyze_response(
        self, analysis: PhotoAnalysis, mime_type: str, image_bytes: int, seconds: float
    ) -> PhotoAnalysisResponse:
        return PhotoAnalysisResponse(
            analysis=analysis,
            metadata=AnalysisMetadata(
                model=self.model,
                image_mime_type=mime_type,
                image_bytes=image_bytes,
                processing_time_seconds=round(seconds, 3),
            ),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_json_object(text: str) -> dict:
        """Parse a JSON object from model output, tolerating code fences."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError as exc:
                    raise UpstreamAIError(
                        "The AI service returned malformed JSON.",
                        code="ai_invalid_response",
                        detail=str(exc),
                    ) from exc
            raise UpstreamAIError(
                "The AI service returned a response that was not JSON.",
                code="ai_invalid_response",
            )

    @staticmethod
    def _mock_guide(plant_data: PlantInputData) -> GeminiResponse:
        """Clearly-labeled offline guide used only when allow_mock_ai=true."""
        mock = {
            "plant_overview": {
                "description": f"{plant_data.plant_name} is a {plant_data.plant_type.lower()} suited to {plant_data.climate.lower()} climates. (Mock guide — set GEMINI_API_KEY for real AI guidance.)",
                "ideal_conditions": {
                    "temperature": "18-24°C (64-75°F)",
                    "humidity": "40-60%",
                    "sunlight": f"{plant_data.sunlight_hours} hours of direct sunlight daily",
                    "soil_ph": "6.0-7.0",
                },
                "benefits": [
                    "Improves air quality",
                    "Adds natural beauty to your space",
                    "Relaxing to care for",
                ],
                "difficulty_level": plant_data.experience_level,
            },
            "growth_stages": [
                {
                    "stage_name": "Germination",
                    "duration": "7-14 days",
                    "care_instructions": "Keep soil moist but not waterlogged. Maintain warm temperature around 20-25°C.",
                    "key_indicators": ["First leaves emerging", "Seed coat splitting"],
                },
                {
                    "stage_name": "Seedling",
                    "duration": "2-4 weeks",
                    "care_instructions": "Provide adequate light and consistent moisture. Begin gentle fertilization.",
                    "key_indicators": ["True leaves developing", "Strong stem growth"],
                },
                {
                    "stage_name": "Vegetative Growth",
                    "duration": "4-8 weeks",
                    "care_instructions": "Increase watering as the plant grows. Provide full sunlight and regular feeding.",
                    "key_indicators": ["Rapid leaf production", "Branching development"],
                },
                {
                    "stage_name": "Maturity",
                    "duration": "Ongoing",
                    "care_instructions": "Maintain a regular routine. Monitor for pests and diseases.",
                    "key_indicators": ["Full size reached", "Flowering/fruiting"],
                },
            ],
            "daily_care": {
                "morning_routine": [
                    "Check soil moisture",
                    "Water if the top inch is dry",
                    "Inspect leaves for pests",
                ],
                "afternoon_routine": [
                    "Ensure adequate sunlight",
                    "Rotate the pot for even light",
                ],
                "evening_routine": [
                    "Mist leaves if humidity is low",
                    "Check for changes in plant health",
                ],
                "weekly_tasks": [
                    "Apply balanced fertilizer during growing season",
                    "Prune dead or damaged growth",
                    "Deep water to flush soil salts",
                ],
            },
            "common_problems": [
                {
                    "problem": "Yellowing Leaves",
                    "symptoms": ["Lower leaves turning yellow", "Slow growth"],
                    "solution": "Check the watering schedule; yellowing often signals over- or under-watering. Ensure drainage.",
                    "prevention": "Water only when the top inch of soil is dry. Use well-draining soil.",
                },
                {
                    "problem": "Pest Infestation",
                    "symptoms": ["Visible insects", "Sticky residue", "Damaged foliage"],
                    "solution": "Spray with neem oil or insecticidal soap; isolate the plant if needed.",
                    "prevention": "Inspect regularly and maintain good air circulation.",
                },
                {
                    "problem": "Root Rot",
                    "symptoms": ["Wilting despite wet soil", "Mushy roots", "Foul odor"],
                    "solution": "Trim affected roots and repot in fresh, well-draining soil.",
                    "prevention": "Use pots with drainage holes and avoid overwatering.",
                },
                {
                    "problem": "Stunted Growth",
                    "symptoms": ["Little new growth", "Small leaves"],
                    "solution": "Check light levels and feeding; repot if root-bound.",
                    "prevention": "Provide adequate light and feed during the growing season.",
                },
            ],
            "additional_tips": [
                "Adjust watering for the season — less in cool, humid weather",
                "Use room-temperature water",
                "Group plants with similar needs together",
                "Take weekly photos to spot problems early",
            ],
        }
        return GeminiResponse.model_validate(mock)

    @staticmethod
    def _mock_analysis() -> PhotoAnalysis:
        return PhotoAnalysis(
            identification=PlantIdentification(
                likely_name="Mock Plant (offline demo)",
                possible_species=["Demo species"],
                confidence="low",
                confidence_reasoning="No AI API key is configured; this is placeholder output (ALLOW_MOCK_AI=true).",
                visible_characteristics=["Not analyzed — mock mode"],
            ),
            observations=[
                VisibleObservation(observation="Not analyzed — mock mode", severity="unclear")
            ],
            possible_causes=["Not analyzed — mock mode"],
            care_recommendations=["Configure GEMINI_API_KEY to enable real photo analysis."],
            follow_up_observations=["Retake the photo with good lighting once AI is configured."],
            source="mock",
        )


def types_part_bytes(image_bytes: bytes, mime_type: str):
    """Build a Gemini content part from raw image bytes (official SDK)."""
    from google.genai import types

    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


# Singleton instance
gemini_service = GeminiService()
