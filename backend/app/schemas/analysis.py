"""
Photo analysis schemas (plant identification + visible symptom assessment).

Design principles:
- Separate *visible observations* from *possible causes* (diagnosis is never
  presented as definitive from a photo alone).
- Confidence is an explicit label with reasoning, not a fake numeric score.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]


class PlantIdentification(BaseModel):
    likely_name: str = Field(..., description="Most likely plant common name")
    possible_species: List[str] = Field(default_factory=list)
    confidence: Confidence
    confidence_reasoning: str = Field(
        ..., description="Why this confidence level was assigned"
    )
    visible_characteristics: List[str] = Field(
        default_factory=list, description="Traits actually visible in the photo"
    )


class VisibleObservation(BaseModel):
    observation: str = Field(..., description="What is visible in the photo")
    severity: Literal["none", "mild", "moderate", "severe", "unclear"] = "unclear"


class PhotoAnalysis(BaseModel):
    identification: PlantIdentification
    observations: List[VisibleObservation] = Field(default_factory=list)
    possible_causes: List[str] = Field(
        default_factory=list,
        description="Possible explanations for observations — not confirmed diagnoses",
    )
    care_recommendations: List[str] = Field(default_factory=list)
    follow_up_observations: List[str] = Field(
        default_factory=list,
        description="What the user should check next to refine the assessment",
    )
    disclaimer: str = (
        "This assessment is generated from a photo by an AI model. It describes "
        "visible characteristics and plausible causes — it is not a definitive "
        "plant identification or plant-health diagnosis. Conditions can look "
        "similar in photos; consult a local nursery or plant specialist when a "
        "problem matters to you."
    )
    source: Literal["gemini", "mock"] = "gemini"


class AnalysisMetadata(BaseModel):
    model: str
    image_mime_type: str
    image_bytes: int
    processing_time_seconds: float


class PhotoAnalysisResponse(BaseModel):
    success: bool = True
    analysis: PhotoAnalysis
    metadata: AnalysisMetadata
