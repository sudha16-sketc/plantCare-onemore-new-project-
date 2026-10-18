import { useState } from 'react';
import PlantForm from './PlantForm.jsx';
import Loading from './Loading.jsx';
import PlantOverview from './PlantOverview.jsx';
import GrowthStages from './GrowthStage.jsx';
import DailyCare from './DailyCare.jsx';
import Problems from './Problem.jsx';
import VisualGuide from './VisualGuide.jsx';
import ExtraTips from './ExtraTips.jsx';

import { useAuth } from '../context/useAuth.js';
import * as api from '../api/client';

import './MainPage.css';

// PlantForm watering_frequency labels → interval days for the collection API
const WATERING_INTERVAL_DAYS = {
  Daily: 1,
  'Every 2-3 days': 3,
  Weekly: 7,
  'Bi-weekly': 14,
  Monthly: 30,
};

function transformGuideResponse(data, plantName) {
  return {
    overview: {
      plant_name: plantName,
      description: data.plant_care_guidance.plant_overview.description,
      difficulty_level: data.plant_care_guidance.plant_overview.difficulty_level,
      ideal_conditions: data.plant_care_guidance.plant_overview.ideal_conditions,
      benefits: data.plant_care_guidance.plant_overview.benefits,
    },
    growth_stages: data.plant_care_guidance.growth_stages.map((stage) => ({
      stage_name: stage.stage_name,
      duration: stage.duration,
      care_instructions: stage.care_instructions,
      key_indicators: stage.key_indicators,
    })),
    daily_care: {
      morning: data.plant_care_guidance.daily_care.morning_routine?.join('\n') || '',
      afternoon: data.plant_care_guidance.daily_care.afternoon_routine?.join('\n') || '',
      evening: data.plant_care_guidance.daily_care.evening_routine?.join('\n') || '',
      weekly_tasks: data.plant_care_guidance.daily_care.weekly_tasks || [],
    },
    common_problems: data.plant_care_guidance.common_problems.map((problem) => ({
      problem: problem.problem,
      symptoms: problem.symptoms?.join('\n') || problem.symptoms,
      solution: problem.solution,
      prevention: problem.prevention,
    })),
    extra_tips: data.plant_care_guidance.additional_tips || [],
    visual_guide: data.visual_guide?.file_url || null,
    ai_source: data.metadata?.ai_source || data.plant_care_guidance?.ai_source || null,
    saved_to_collection: false,
  };
}

function MainPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [plantGuide, setPlantGuide] = useState(null);
  const [progress, setProgress] = useState(0);
  const { user } = useAuth();

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setPlantGuide(null);
    setProgress(0);

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
      const response = await api.generatePlantGuide(data);
      setProgress(100);

      let guide = transformGuideResponse(response, data.plant_name);

      // Save the plant to the user's server-side collection when signed in
      if (user) {
        try {
          await api.createPlant({
            name: data.plant_name,
            species: data.plant_type || null,
            climate: data.climate || null,
            soil_type: data.soil_type || null,
            sunlight: `${data.sunlight_hours} hours`,
            watering_interval_days:
              WATERING_INTERVAL_DAYS[data.watering_frequency] || 7,
            care_notes: `Experience level: ${data.experience_level}`,
          });
          guide = { ...guide, saved_to_collection: true };
        } catch {
          // Non-fatal: the guide itself succeeded
        }
      }

      setTimeout(() => {
        setPlantGuide(guide);
        setLoading(false);
      }, 300);
    } catch (err) {
      setError(err.message || 'Something went wrong. Try again.');
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
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
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
                aria-hidden="true"
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

            {plantGuide.ai_source === 'mock' && (
              <p className="guide-notice" role="note">
                Demo mode: this guide was produced by the mock AI service, not
                the live model.
              </p>
            )}
            {plantGuide.saved_to_collection && (
              <p className="guide-notice success" role="status">
                Saved to <strong>My Plants</strong> with a watering reminder.
              </p>
            )}

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
      </main>
    </div>
  );
}

export default MainPage;
