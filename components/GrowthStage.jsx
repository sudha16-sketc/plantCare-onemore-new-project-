import './GrowthStage.css';

const GrowthStages = ({ stages }) => {
  if (!stages || stages.length === 0) return null;

  return (
    <div className="growth-stages">
      <h2 className="stages-title">Growth Stages Timeline</h2>
      <p className="stages-subtitle">Track your plant's journey from seed to maturity</p>
      
      <div className="timeline">
        {stages.map((stage, index) => (
          <div key={index} className="timeline-item" style={{ animationDelay: `${index * 0.15}s` }}>
            <div className="timeline-marker">
              <div className="marker-dot">{index + 1}</div>
              {index < stages.length - 1 && <div className="marker-line"></div>}
            </div>
            
            <div className="timeline-content">
              <div className="stage-header">
                <h3 className="stage-name">{stage.stage_name}</h3>
                {stage.duration && (
                  <span className="stage-duration">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    {stage.duration}
                  </span>
                )}
              </div>
              
              <div className="stage-care">
                <h4 className="care-heading">Care Instructions</h4>
                <p className="care-text">{stage.care_instructions}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GrowthStages;