"""
Pydantic schemas for request and response validation.
These models ensure type safety and automatic validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional


class PlantInputData(BaseModel):
    """
    Schema for plant input data received from the frontend.
    
    Validates all required fields for generating plant care guidance.
    """
    
    plant_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the plant (e.g., 'Tomato', 'Rose')"
    )
    
    plant_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of plant (e.g., 'Vegetable', 'Flower', 'Herb')"
    )
    
    climate: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Climate zone (e.g., 'Tropical', 'Temperate', 'Arid')"
    )
    
    sunlight_hours: int = Field(
        ...,
        ge=0,
        le=24,
        description="Daily sunlight hours (0-24)"
    )
    
    soil_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Soil type (e.g., 'Loamy', 'Clay', 'Sandy')"
    )
    
    watering_frequency: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Watering frequency (e.g., 'Daily', 'Weekly', 'Bi-weekly')"
    )
    
    experience_level: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Gardener's experience level (e.g., 'Beginner', 'Intermediate', 'Advanced')"
    )
    
    @validator('plant_name', 'plant_type', 'climate', 'soil_type', 'watering_frequency', 'experience_level')
    def trim_whitespace(cls, v):
        """Remove leading and trailing whitespace from string fields."""
        return v.strip() if isinstance(v, str) else v
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "plant_name": "Tomato",
                "plant_type": "Vegetable",
                "climate": "Temperate",
                "sunlight_hours": 6,
                "soil_type": "Loamy",
                "watering_frequency": "Daily",
                "experience_level": "Beginner"
            }
        }
    


class GrowthStage(BaseModel):
    """Schema for individual growth stage information."""
    
    stage_name: str
    duration: str
    care_instructions: str
    key_indicators: List[str]


class Problem(BaseModel):
    """Schema for common plant problems and solutions."""
    
    problem: str
    symptoms: List[str]
    solution: str
    prevention: str


class PlantOverview(BaseModel):
    """Schema for plant overview information."""
    
    description: str
    ideal_conditions: Dict[str, str]  # Dict with string keys and values for better type safety
    benefits: List[str]
    difficulty_level: str


class DailyCare(BaseModel):
    """Schema for daily care tips."""
    
    morning_routine: List[str]
    afternoon_routine: List[str]
    evening_routine: List[str]
    weekly_tasks: List[str]


class GeminiResponse(BaseModel):
    """
    Schema for the structured response from Gemini AI.
    
    Contains comprehensive plant care guidance.
    """
    
    plant_overview: PlantOverview
    growth_stages: List[GrowthStage]
    daily_care: DailyCare
    common_problems: List[Problem]
    additional_tips: List[str]


class NotebookLMResponse(BaseModel):
    """
    Schema for NotebookLM response.
    
    Contains visual guide information.
    """
    
    status: str
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    message: str


class PlantGuideResponse(BaseModel):
    """
    Final API response combining Gemini and NotebookLM outputs.
    
    This is the complete response sent to the frontend.
    """
    
    success: bool
    plant_care_guidance: GeminiResponse
    visual_guide: NotebookLMResponse
    metadata: Dict[str, Any]
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "success": True,
                "plant_care_guidance": {
                    "plant_overview": {
                        "description": "Comprehensive plant information",
                        "ideal_conditions": {},
                        "benefits": [],
                        "difficulty_level": "Beginner"
                    },
                    "growth_stages": [],
                    "daily_care": {
                        "morning_routine": [],
                        "afternoon_routine": [],
                        "evening_routine": [],
                        "weekly_tasks": []
                    },
                    "common_problems": [],
                    "additional_tips": []
                },
               "visual_guide": {
                    "status": "success",
                    "file_url": "https://example.com/guide.pptx",
                    "file_type": "pptx",
                    "message": "Visual guide generated successfully"
                },
               "metadata": {
                    "timestamp": "2026-01-27T10:00:00Z",
                    "processing_time_seconds": 2.5
                }
            }
        }
    


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response."""
    
    status: str
    message: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None