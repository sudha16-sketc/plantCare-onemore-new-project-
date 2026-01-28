"""
Gemini AI Service Module

This module handles all interactions with the Google Gemini AI API.
It constructs prompts, sends requests, and parses structured JSON responses.
"""
import json

import httpx
import os
from typing import Dict, Any
from app.schemas.plant import PlantInputData, GeminiResponse
import re


# Configuration
API_KEY = os.getenv("GEMINI_API_KEY", "")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"


class GeminiService:
    """
    Service class for interacting with Google Gemini AI.

    Handles prompt construction, API communication, and response parsing.
    """
    
    def __init__(self):
        """Initialize Gemini service with API configuration."""
        self.api_key = API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        self.timeout = 30.0
    
    def _build_prompt(self, plant_data: PlantInputData) -> str:
        """
        Build a structured prompt for Gemini AI based on plant data.
        
        Args:
            plant_data: Validated plant input data
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert botanist and plant care specialist. Based on the following plant information, 
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

        return prompt
    
    async def generate_plant_guide(self, plant_data: PlantInputData) -> GeminiResponse:
        """
        Generate comprehensive plant care guidance using Gemini AI.
        
        Args:
            plant_data: Validated plant input data
            
        Returns:
            Structured Gemini response with plant care guidance
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        if not self.api_key:
            # Return mock response if no API key is configured
            return self._generate_mock_response(plant_data)
        
        try:
            # Build the prompt
            prompt = self._build_prompt(plant_data)
            
            # Prepare API request
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            # Make async API call
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()


            
            # Parse response
            result = response.json()
            
            if DEBUG_MODE:
                print("Gemini raw response:", result)
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                try:
                    parts = result["candidates"][0]["content"]["parts"]
                    text_content = "".join(p.get("text", "") for p in parts)
                except (KeyError, IndexError):
                    raise Exception("Malformed Gemini response")

                
                # Clean up markdown formatting if present
                text_content = text_content.strip()
                text_content = text_content.removeprefix("```json")
                text_content = text_content.removeprefix("```")
                text_content = text_content.removesuffix("```")
                text_content = text_content.strip()
                text_content = re.sub(r"```(?:json)?", "", text_content)
                text_content = text_content.strip()

                
                # Parse JSON response
                json_response = json.loads(text_content)
                
                # Validate and return as Pydantic model
                return GeminiResponse(**json_response)
            else:
                raise Exception("No valid response from Gemini API")
                
        except httpx.HTTPError as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Gemini service failed: {str(e)}") from e

    
    def _generate_mock_response(self, plant_data: PlantInputData) -> GeminiResponse:
        """
        Generate a mock response for testing without API key.
        
        Args:
            plant_data: Plant input data
            
        Returns:
            Mock Gemini response
        """
        mock_data = {
            "plant_overview": {
                "description": f"{plant_data.plant_name} is a wonderful {plant_data.plant_type.lower()} that thrives in {plant_data.climate.lower()} climates. It's well-suited for gardeners of all levels and provides both aesthetic beauty and practical benefits.",
                "ideal_conditions": {
                    "temperature": "18-24°C (64-75°F)",
                    "humidity": "40-60%",
                    "sunlight": f"{plant_data.sunlight_hours} hours of direct sunlight daily",
                    "soil_ph": "6.0-7.0"
                },
                "benefits": [
                    "Improves air quality",
                    "Adds natural beauty to your space",
                    "Provides fresh produce/flowers"
                ],
                "difficulty_level": plant_data.experience_level
            },
            "growth_stages": [
                {
                    "stage_name": "Germination",
                    "duration": "7-14 days",
                    "care_instructions": "Keep soil moist but not waterlogged. Maintain warm temperature around 20-25°C.",
                    "key_indicators": ["First leaves emerging", "Seed coat splitting", "Root development visible"]
                },
                {
                    "stage_name": "Seedling",
                    "duration": "2-4 weeks",
                    "care_instructions": "Provide adequate light and maintain consistent moisture. Begin gentle fertilization.",
                    "key_indicators": ["True leaves developing", "Strong stem growth", "Established root system"]
                },
                {
                    "stage_name": "Vegetative Growth",
                    "duration": "4-8 weeks",
                    "care_instructions": "Increase watering as plant grows. Provide full sunlight and regular feeding.",
                    "key_indicators": ["Rapid leaf production", "Stem thickening", "Branching development"]
                },
                {
                    "stage_name": "Maturity",
                    "duration": "Ongoing",
                    "care_instructions": "Maintain regular care routine. Monitor for pests and diseases. Harvest as appropriate.",
                    "key_indicators": ["Full size reached", "Flowering/fruiting", "Strong established growth"]
                }
            ],
            "daily_care": {
                "morning_routine": [
                    "Check soil moisture level",
                    "Water if soil is dry to touch",
                    "Inspect leaves for pests or disease",
                    "Remove any dead or yellowing leaves"
                ],
                "afternoon_routine": [
                    "Ensure adequate sunlight exposure",
                    "Rotate plant for even light distribution",
                    "Check temperature conditions"
               ],
                "evening_routine": [
                    "Mist leaves if humidity is low",
                    "Check for any changes in plant health",
                    "Prepare for next day's care"
                ],
                "weekly_tasks": [
                    "Apply balanced fertilizer",
                    "Prune dead or damaged growth",
                    "Check and adjust support structures",
                    "Deep water to flush soil",
                    "Inspect root health through drainage holes"
                ]
            },
            "common_problems": [
                {
                    "problem": "Yellowing Leaves",
                    "symptoms": ["Lower leaves turning yellow", "Slow growth", "Pale coloration"],
                    "solution": "Check watering schedule and adjust. May indicate overwatering or nitrogen deficiency. Ensure proper drainage.",
                    "prevention": "Water only when top inch of soil is dry. Use well-draining soil mix. Fertilize regularly during growing season."
                },
                {
                    "problem": "Pest Infestation",
                    "symptoms": ["Visible insects on leaves", "Sticky residue", "Damaged or eaten foliage"],
                    "solution": "Spray with neem oil solution or insecticidal soap. Remove heavily infested leaves. Isolate plant if necessary.",
                    "prevention": "Regular inspection of plants. Maintain good air circulation. Keep growing area clean. Quarantine new plants."
               },
                {
                    "problem": "Root Rot",
                    "symptoms": ["Wilting despite wet soil", "Brown mushy roots", "Foul odor from soil"],
                    "solution": "Remove plant from pot, trim affected roots, repot in fresh soil with better drainage. Reduce watering frequency.",
                    "prevention": "Use pots with drainage holes. Don't overwater. Ensure soil has good drainage. Allow soil to dry between waterings."
                },
                {
                    "problem": "Stunted Growth",
                   "symptoms": ["Little to no new growth", "Small leaf size", "Weak stems"],
                    "solution": "Check light levels and increase if needed. Apply appropriate fertilizer. Check for root-bound conditions.",
                    "prevention": "Provide adequate light. Feed regularly during growing season. Repot when roots fill container. Maintain proper temperature."
                }
            ],
            "additional_tips": [
                f"Adjust watering based on {plant_data.climate} climate conditions - less in humid weather, more in dry conditions",
                f"Given your {plant_data.experience_level.lower()} experience level, start with consistent routines and keep a plant journal",
                f"The {plant_data.soil_type.lower()} soil is good, but consider adding compost for nutrients",
                "Group plants with similar needs together for easier care",
                "Use room-temperature water to avoid shocking the roots",
                "Consider using mulch to retain moisture and regulate soil temperature",
               "Take photos weekly to track growth progress and spot problems early"
            ]
        }
        
        return GeminiResponse(**mock_data)


# Singleton instance
gemini_service = GeminiService()