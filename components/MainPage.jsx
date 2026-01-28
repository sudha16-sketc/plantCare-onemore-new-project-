import { useState, useEffect } from "react";
import React from "react";
import PlantForm from "./PlantForm.jsx";
import Loading from "./Loading.jsx";
import PlantOverview from "./PlantOverview.jsx";
import GrowthStages from "./GrowthStage.jsx";
import DailyCare from "./DailyCare.jsx";
import Problems from "./Problem.jsx";
import VisualGuide from "./VisualGuide.jsx";
import ExtraTips from "./ExtraTips.jsx";
import SlideDesign from "./SlideDesign.jsx";

import "./MainPage.css";

/**
 * PlantCare Frontend Application
 *
 * This React app integrates with the FastAPI backend to provide
 * AI-powered plant care guidance using multiple services.
 *
 * Architecture:
 * 1. User fills out plant information form  * 2. Frontend sends request to backend API  * 3. Backend calls Gemini AI for guidance generation
 * 4. Backend generates PPT with visual guide
 * 5. Frontend displays comprehensive care guide
 *
 * Environment:
 * - REACT_APP_API_URL: Backend API endpoint (default: http://localhost:8000)
 * - Set in .env.local file
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const generatePlantGuide = async (formData) => {
  try {
    // Transform frontend form data to match backend schema
    const payload = {
      plant_name: formData.plant_name,
      plant_type: formData.plant_type,
      climate: formData.climate,
      sunlight_hours: parseInt(formData.sunlight_hours, 10),
      soil_type: formData.soil_type,
      watering_frequency: formData.watering_frequency,
      experience_level: formData.experience_level,
    };

    console.log("Sending request to backend:", payload);

    const response = await fetch(`${API_BASE_URL}/generate-plant-guide`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage =
        errorData.detail || errorData.error || `HTTP ${response.status}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log("Received response from backend:", data);

    // Transform backend response to frontend format
    return {
      overview: {
        plant_name: formData.plant_name,
        description: data.plant_care_guidance.plant_overview.description,
        difficulty_level:
          data.plant_care_guidance.plant_overview.difficulty_level,
        ideal_conditions:
          data.plant_care_guidance.plant_overview.ideal_conditions,
        benefits: data.plant_care_guidance.plant_overview.benefits,
      },
      growth_stages: data.plant_care_guidance.growth_stages.map((stage) => ({
        stage_name: stage.stage_name,
        duration: stage.duration,
        care_instructions: stage.care_instructions,
        key_indicators: stage.key_indicators,
      })),
      daily_care: {
        morning:
          data.plant_care_guidance.daily_care.morning_routine?.join("\n") || "",
        afternoon:
          data.plant_care_guidance.daily_care.afternoon_routine?.join("\n") ||
          "",
        evening:
          data.plant_care_guidance.daily_care.evening_routine?.join("\n") || "",
        weekly_tasks: data.plant_care_guidance.daily_care.weekly_tasks || [],
      },
      common_problems: data.plant_care_guidance.common_problems.map(
        (problem) => ({
          problem: problem.problem,
          symptoms: problem.symptoms?.join("\n") || problem.symptoms,
          solution: problem.solution,
          prevention: problem.prevention,
        }),
      ),
      extra_tips: data.plant_care_guidance.additional_tips || [],
      visual_guide: data.visual_guide?.file_url || null,
    };
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

function MainPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [plantGuide, setPlantGuide] = useState(null);
  const [progress, setProgress] = useState(0);
  const [apiStatus, setApiStatus] = useState("unknown");

  // Check API health on component mount
  React.useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setApiStatus(response.ok ? "online" : "error");
    } catch (err) {
      console.warn("API status check failed:", err);
      setApiStatus("offline");
    }
  };

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setPlantGuide(null);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      const data = await generatePlantGuide(formData);
      setProgress(100);
      setTimeout(() => {
        setPlantGuide(data);
        setLoading(false);
      }, 300);
    } catch (err) {
      console.error("Error generating guide:", err);
      setError(err.message || "Something went wrong. Try again.");
      setLoading(false);
      clearInterval(progressInterval);
    }
  };

  const handleReset = () => {
    setPlantGuide(null);
    setError(null);
    setProgress(0);
  };

  return (
    <div className="app">
      <main className="app-main">
        {!plantGuide && !loading && (
          <div className="form-container">
            <PlantForm onSubmit={handleSubmit} />
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <Loading progress={progress} />
          </div>
        )}

        {error && (
          <div className="error-container">
            <div className="error-message">
              <svg
                className="error-icon"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <path
                  d="M12 8V12M12 16H12.01"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              <p>{error}</p>
            </div>
            <button className="retry-button" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}

        {plantGuide && (
          <div className="guide-container">
            <button className="new-guide-button" onClick={handleReset}>
              <svg
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 5V19M5 12H19"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              Create New Guide
            </button>

            <div className="guide-content">
              <PlantOverview data={plantGuide.overview} />
              <GrowthStages stages={plantGuide.growth_stages} />
              <DailyCare care={plantGuide.daily_care} />
              <Problems problems={plantGuide.common_problems} />
              <ExtraTips tips={plantGuide.extra_tips} />
              {plantGuide.visual_guide && (
                <VisualGuide visualGuide={plantGuide.visual_guide} />
              )}
            </div>
          </div>
        )}
      <SlideDesign />
      </main>
    </div>
  );
}

export default MainPage;
