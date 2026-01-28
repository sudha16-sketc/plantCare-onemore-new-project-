import { useState } from 'react';
import './PlantForm.css';

const PlantForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    plant_name: '',
    plant_type: '',
    climate: '',
    sunlight_hours: 6,
    soil_type: '',
    watering_frequency: '',
    experience_level: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const isFormValid = () => {
    return Object.values(formData).every(value => value !== '');
  };

  return (
    <form className="plant-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h2 className="form-title">Tell us about your plant</h2>
        <p className="form-subtitle">Share some details and we'll create a personalized care guide</p>
      </div>

      <div className="form-grid">
        {/* Plant Name */}
        <div className="form-group full-width">
          <label htmlFor="plant_name" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L12 22M12 2C12 2 8 6 8 10C8 11.0609 8.42143 12.0783 9.17157 12.8284C9.92172 13.5786 10.9391 14 12 14C13.0609 14 14.0783 13.5786 14.8284 12.8284C15.5786 12.0783 16 11.0609 16 10C16 6 12 2 12 2Z" stroke="currentColor" strokeWidth="2"/>
            </svg>
            Plant Name
          </label>
          <input
            type="text"
            id="plant_name"
            name="plant_name"
            value={formData.plant_name}
            onChange={handleChange}
            placeholder="e.g., Tomato, Rose, Snake Plant..."
            className="form-input"
            required
          />
        </div>

        {/* Plant Type */}
        <div className="form-group">
          <label htmlFor="plant_type" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 20H21M5 20V10L12 3L19 10V20M9 20V14H15V20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Plant Type
          </label>
          <select
            id="plant_type"
            name="plant_type"
            value={formData.plant_type}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Select type</option>
            <option value="Vegetable">Vegetable</option>
            <option value="Flower">Flower</option>
            <option value="Indoor">Indoor</option>
            <option value="Medicinal">Medicinal</option>
          </select>
        </div>

        {/* Climate */}
        <div className="form-group">
          <label htmlFor="climate" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 1V3M12 21V23M23 12H21M3 12H1M20.5 20.5L18.5 18.5M5.5 5.5L3.5 3.5M20.5 3.5L18.5 5.5M5.5 18.5L3.5 20.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Climate
          </label>
          <select
            id="climate"
            name="climate"
            value={formData.climate}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Select climate</option>
            <option value="Tropical">Tropical</option>
            <option value="Temperate">Temperate</option>
            <option value="Arid">Arid</option>
            <option value="Humid">Humid</option>
          </select>
        </div>

        {/* Sunlight Hours */}
        <div className="form-group full-width">
          <label htmlFor="sunlight_hours" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="4" fill="currentColor"/>
              <path d="M12 2V6M12 18V22M22 12H18M6 12H2M19.07 4.93L16.24 7.76M7.76 16.24L4.93 19.07M19.07 19.07L16.24 16.24M7.76 7.76L4.93 4.93" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Sunlight Hours per Day: <span className="sunlight-value">{formData.sunlight_hours}h</span>
          </label>
          <div className="slider-container">
            <input
              type="range"
              id="sunlight_hours"
              name="sunlight_hours"
              min="0"
              max="12"
              value={formData.sunlight_hours}
              onChange={handleChange}
              className="form-slider"
              required
            />
            <div className="slider-labels">
              <span>0h</span>
              <span>6h</span>
              <span>12h</span>
            </div>
          </div>
        </div>

        {/* Soil Type */}
        <div className="form-group">
          <label htmlFor="soil_type" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 11V8C6 6 7 4 9 3C11 2 13 2 15 3C17 4 18 6 18 8V11" stroke="currentColor" strokeWidth="2"/>
            </svg>
            Soil Type
          </label>
          <select
            id="soil_type"
            name="soil_type"
            value={formData.soil_type}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Select soil type</option>
            <option value="Loamy">Loamy</option>
            <option value="Sandy">Sandy</option>
            <option value="Clay">Clay</option>
            <option value="Peaty">Peaty</option>
            <option value="Chalky">Chalky</option>
            <option value="Silty">Silty</option>
          </select>
        </div>

        {/* Watering Frequency */}
        <div className="form-group">
          <label htmlFor="watering_frequency" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2.69L17.66 8.35C18.45 9.14 19 10.18 19 11.5C19 14.26 16.76 16.5 14 16.5H10C7.24 16.5 5 14.26 5 11.5C5 10.18 5.55 9.14 6.34 8.35L12 2.69Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 16.5V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Watering Frequency
          </label>
          <select
            id="watering_frequency"
            name="watering_frequency"
            value={formData.watering_frequency}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Select frequency</option>
            <option value="Daily">Daily</option>
            <option value="Every 2-3 days">Every 2-3 days</option>
            <option value="Weekly">Weekly</option>
            <option value="Bi-weekly">Bi-weekly</option>
            <option value="Monthly">Monthly</option>
          </select>
        </div>

        {/* Experience Level */}
        <div className="form-group full-width">
          <label htmlFor="experience_level" className="form-label">
            <svg className="label-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Your Experience Level
          </label>
          <div className="experience-options">
            {['Beginner', 'Intermediate', 'Advanced'].map(level => (
              <label key={level} className={`experience-card ${formData.experience_level === level ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="experience_level"
                  value={level}
                  checked={formData.experience_level === level}
                  onChange={handleChange}
                  className="experience-radio"
                  required
                />
                <span className="experience-label">{level}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <button 
        type="submit" 
        className={`submit-button ${!isFormValid() ? 'disabled' : ''}`}
        disabled={!isFormValid()}
      >
        <svg className="button-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="currentColor"/>
        </svg>
        Generate Plant Care Guide
      </button>
    </form>
  );
};

export default PlantForm;