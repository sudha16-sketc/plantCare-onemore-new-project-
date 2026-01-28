"""
Response Formatter Module

This module combines outputs from different services (Gemini, NotebookLM)
into a unified, clean JSON response for the frontend.
"""

from datetime import datetime
from typing import Dict, Any
from app.schemas.plant import (
    PlantInputData,
    GeminiResponse,
    NotebookLMResponse,
    PlantGuideResponse
)


class ResponseFormatter:
    """
    Formats and combines multiple service responses into final API response.
    """
    
    @staticmethod
    def format_plant_guide_response(
        plant_data: PlantInputData,
        gemini_response: GeminiResponse,
        notebooklm_response: NotebookLMResponse,
        processing_time: float
    ) -> PlantGuideResponse:
        """
        Combine Gemini and NotebookLM responses into final API response.
        
        Args:
            plant_data: Original plant input data
            gemini_response: Plant care guidance from Gemini
            notebooklm_response: Visual guide from NotebookLM
            processing_time: Total processing time in seconds
            
        Returns:
            Complete plant guide response
        """
        # Build metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "processing_time_seconds": round(processing_time, 2),
            "plant_name": plant_data.plant_name,
            "plant_type": plant_data.plant_type,
            "ai_model": "gemini-pro",
            "version": "1.0.0"
        }
        
        # Create complete response
        return PlantGuideResponse(
            success=True,
            plant_care_guidance=gemini_response,
            visual_guide=notebooklm_response,
            metadata=metadata
        )
    
    @staticmethod
    def format_error_response(
        error_message: str,
        detail: str = None
    ) -> Dict[str, Any]:
        """
        Format error response with consistent structure.
        
        Args:
            error_message: Main error message
            detail: Optional detailed error information
            
        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "error": error_message,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def enhance_response_with_insights(
        response: PlantGuideResponse,
        plant_data: PlantInputData
    ) -> PlantGuideResponse:
        """
        Add personalized insights based on plant data.
        
        Args:
            response: Base plant guide response
            plant_data: Original plant input data
            
        Returns:
            Enhanced response with additional insights
        """
        # Add personalized insights to metadata
        insights = []
        
        # Sunlight insights
        if plant_data.sunlight_hours < 4:
            insights.append("Consider supplemental grow lights for low-light conditions")
        elif plant_data.sunlight_hours > 8:
            insights.append("Monitor for sun stress during peak hours")
        
        # Experience level insights
        if plant_data.experience_level.lower() == "beginner":
            insights.append("Focus on establishing consistent care routines")
            insights.append("Keep a plant journal to track progress")
        
        # Climate insights
        if plant_data.climate.lower() in ["tropical", "humid"]:
            insights.append("Ensure good air circulation to prevent fungal issues")
        elif plant_data.climate.lower() in ["arid", "dry"]:
            insights.append("Consider humidity trays or misting for moisture")
        
        # Add insights to metadata
        if insights:
            response.metadata["personalized_insights"] = insights
        
        return response


# Singleton instance
response_formatter = ResponseFormatter()