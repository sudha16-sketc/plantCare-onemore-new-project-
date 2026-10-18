import './Loading.css';

const Loading = ({ progress = 0 }) => {
  return (
    <div className="loading">
      <div className="loading-content">
        <div className="plant-loader">
          <svg className="plant-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            {/* Stem */}
            <line x1="50" y1="50" x2="50" y2="100" stroke="currentColor" strokeWidth="3" className="stem"/>
            
            {/* Left Leaf */}
            <path 
              d="M 50 70 Q 30 60 25 45 Q 30 50 50 60" 
              fill="currentColor" 
              className="leaf leaf-left"
            />
            
            {/* Right Leaf */}
            <path 
              d="M 50 60 Q 70 50 75 35 Q 70 40 50 50" 
              fill="currentColor" 
              className="leaf leaf-right"
            />
            
            {/* Top Leaf */}
            <path 
              d="M 50 50 Q 45 30 50 15 Q 55 30 50 45" 
              fill="currentColor" 
              className="leaf leaf-top"
            />
            
            {/* Flower */}
            <circle cx="50" cy="25" r="8" fill="currentColor" className="flower"/>
          </svg>
        </div>
        
        <h3 className="loading-title">AI is analyzing your plant...</h3>
        <p className="loading-text">Preparing a personalized care guide</p>
        
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            >
              <div className="progress-shine"></div>
            </div>
          </div>
          <span className="progress-percentage">{progress}%</span>
        </div>
        
        <div className="loading-steps">
          <div className={`step ${progress >= 25 ? 'active' : ''}`}>
            <div className="step-icon">🌱</div>
            <span>Analyzing plant</span>
          </div>
          <div className={`step ${progress >= 50 ? 'active' : ''}`}>
            <div className="step-icon">☀️</div>
            <span>Checking conditions</span>
          </div>
          <div className={`step ${progress >= 75 ? 'active' : ''}`}>
            <div className="step-icon">💧</div>
            <span>Creating schedule</span>
          </div>
          <div className={`step ${progress >= 100 ? 'active' : ''}`}>
            <div className="step-icon">📋</div>
            <span>Finalizing guide</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Loading;