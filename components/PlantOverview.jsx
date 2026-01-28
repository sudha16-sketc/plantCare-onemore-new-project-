import './PlantOverview.css';

const PlantOverview = ({ data }) => {
  if (!data) return null;

  const getDifficultyColor = (difficulty) => {
    const lower = difficulty?.toLowerCase() || '';
    if (lower.includes('easy') || lower.includes('beginner')) return 'easy';
    if (lower.includes('moderate') || lower.includes('intermediate')) return 'moderate';
    if (lower.includes('hard') || lower.includes('advanced')) return 'hard';
    return 'moderate';
  };

  return (
    <div className="plant-overview">
      <div className="overview-header">
        <div className="plant-icon-large">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L12 22M12 2C12 2 8 6 8 10C8 11.0609 8.42143 12.0783 9.17157 12.8284C9.92172 13.5786 10.9391 14 12 14C13.0609 14 14.0783 13.5786 14.8284 12.8284C15.5786 12.0783 16 11.0609 16 10C16 6 12 2 12 2Z" fill="currentColor"/>
            <circle cx="12" cy="8" r="3" fill="white" opacity="0.3"/>
          </svg>
        </div>
        <div className="header-text">
          <h2 className="plant-name">{data.plant_name}</h2>
          <div className={`difficulty-badge ${getDifficultyColor(data.difficulty_level)}`}>
            {data.difficulty_level}
          </div>
        </div>
      </div>

      <div className="overview-content">
        <div className="description-section">
          <h3 className="section-title">About Your Plant</h3>
          <p className="description-text">{data.description}</p>
        </div>

        {data.ideal_conditions && (
          <div className="conditions-section">
            <h3 className="section-title">Ideal Growing Conditions</h3>
            <div className="conditions-grid">
              {(data.ideal_conditions.temperature || data.ideal_conditions.Temperature) && (
                <div className="condition-card">
                  <div className="condition-icon">🌡️</div>
                  <div className="condition-details">
                    <span className="condition-label">Temperature</span>
                    <span className="condition-value">{data.ideal_conditions.temperature || data.ideal_conditions.Temperature}</span>
                  </div>
                </div>
              )}
              {(data.ideal_conditions.humidity || data.ideal_conditions.Humidity) && (
                <div className="condition-card">
                  <div className="condition-icon">💧</div>
                  <div className="condition-details">
                    <span className="condition-label">Humidity</span>
                    <span className="condition-value">{data.ideal_conditions.humidity || data.ideal_conditions.Humidity}</span>
                  </div>
                </div>
              )}
              {(data.ideal_conditions.light || data.ideal_conditions.sunlight || data.ideal_conditions.Light) && (
                <div className="condition-card">
                  <div className="condition-icon">☀️</div>
                  <div className="condition-details">
                    <span className="condition-label">Light</span>
                    <span className="condition-value">{data.ideal_conditions.light || data.ideal_conditions.sunlight || data.ideal_conditions.Light}</span>
                  </div>
                </div>
              )}
              {(data.ideal_conditions.soil_ph || data.ideal_conditions.soil_pH) && (
                <div className="condition-card">
                  <div className="condition-icon">🌱</div>
                  <div className="condition-details">
                    <span className="condition-label">Soil pH</span>
                    <span className="condition-value">{data.ideal_conditions.soil_ph || data.ideal_conditions.soil_pH}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlantOverview;