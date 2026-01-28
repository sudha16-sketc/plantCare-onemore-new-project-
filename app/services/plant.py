"""
API Routes Module

Defines all API endpoints for the Smart Plant Growth Assistant.
Handles request validation, service orchestration, and response formatting.
"""

import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.schemas.plant import (
    PlantInputData,
    PlantGuideResponse,
    HealthCheckResponse,
    ErrorResponse
)
from app.routes.gemini import gemini_service
from app.services.ppt_service import ppt_service
from typing import Optional

# Create router
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status with API version
    """
    return HealthCheckResponse(
        status="healthy",
        message="Smart Plant Growth Assistant API is running",
        version="1.0.0"
    )


@router.post(
    "/generate-plant-guide",
    response_model=PlantGuideResponse,
    summary="Generate Plant Care Guide",
    description="Generate comprehensive plant care guidance using AI",
    responses={
        200: {
            "description": "Successfully generated plant care guide",
            "model": PlantGuideResponse
        },
        400: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def generate_plant_guide(plant_data: PlantInputData):
    """
    Main endpoint to generate comprehensive plant care guidance.
    
    This endpoint orchestrates the entire AI workflow:
    1. Validates input data (handled by Pydantic)
    2. Calls Gemini AI to generate plant care guidance
    3. Calls PPT Service to generate visual guide
    4. Combines and formats the response
    
    Args:
        plant_data: Validated plant information
        
    Returns:
        Complete plant care guide with visual assets
        
    Raises:
        HTTPException: If any step in the process fails
    """
    start_time = time.time()
    
    try:
        # Step 1: Generate plant care guidance using Gemini AI
        print(f"Generating plant guide for: {plant_data.plant_name}")
        gemini_response = await gemini_service.generate_plant_guide(plant_data)
        
        # Step 2: Generate visual guide using PPT Service
        print(f"Generating visual guide for: {plant_data.plant_name}")
        ppt_response = await ppt_service.generate(
            gemini_response,
            plant_data.plant_name
        )
        
        # Step 3: Calculate processing time
        processing_time = time.time() - start_time
        
        # Step 4: Format and combine responses
        final_response = PlantGuideResponse(
            success=True,
            plant_care_guidance=gemini_response,
            visual_guide=ppt_response,
            metadata={
                "plant_name": plant_data.plant_name,
                "plant_type": plant_data.plant_type,
                "climate": plant_data.climate,
                "sunlight_hours": plant_data.sunlight_hours,
                "soil_type": plant_data.soil_type,
                "watering_frequency": plant_data.watering_frequency,
                "experience_level": plant_data.experience_level,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "processing_time_seconds": round(processing_time, 2)
            }
        )
        
        print(f"Successfully generated guide in {processing_time:.2f} seconds")
        return final_response
        
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error generating plant guide: {str(e)}")
        
        # Raise HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plant care guide: {str(e)}"
        )


@router.get(
    "/",
    summary="API Root",
    description="Get basic API information"
)
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Basic API information and available endpoints
    """
    return {
        "name": "Smart Plant Growth Assistant API",
        "version": "1.0.0",
        "description": "AI-powered plant care guidance system",
        "endpoints": {
            "health": "/health",
            "generate_guide": "/generate-plant-guide",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "documentation": "/docs"
    }