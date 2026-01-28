import './Problem.css';

const Problems = ({ problems }) => {
  if (!problems || problems.length === 0) return null;

  const problemIcons = ['🐛', '🍂', '💧', '⚠️', '🔬', '🌡️'];

  // Helper function to format symptoms
  const formatSymptoms = (symptoms) => {
    if (typeof symptoms === 'string') {
      return symptoms.split('\n').filter(s => s.trim());
    }
    return Array.isArray(symptoms) ? symptoms : [symptoms];
  };

  return (
    <div className="problems">
      <h2 className="problems-title">Common Problems & Solutions</h2>
      <p className="problems-subtitle">Be prepared to handle these potential issues</p>

      <div className="problems-grid">
        {problems.map((problem, index) => (
          <div 
            key={index} 
            className="problem-card"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="problem-icon">
              {problemIcons[index % problemIcons.length]}
            </div>

            <div className="problem-content">
              <h3 className="problem-name">{problem.problem}</h3>

              {problem.symptoms && (
                <div className="problem-section">
                  <h4 className="section-label">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 8V12M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Symptoms
                  </h4>
                  <div className="section-text">
                    {typeof problem.symptoms === 'string' ? (
                      <p>{problem.symptoms}</p>
                    ) : Array.isArray(problem.symptoms) ? (
                      <ul>
                        {problem.symptoms.map((symptom, idx) => (
                          <li key={idx}>{symptom}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>{problem.symptoms}</p>
                    )}
                  </div>
                </div>
              )}

              {problem.solution && (
                <div className="problem-section">
                  <h4 className="section-label solution">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Solution
                  </h4>
                  <p className="section-text">{problem.solution}</p>
                </div>
              )}

              {problem.prevention && (
                <div className="problem-section">
                  <h4 className="section-label prevention">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L3 7L12 12L21 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M3 17L12 22L21 17M3 12L12 17L21 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Prevention
                  </h4>
                  <p className="section-text">{problem.prevention}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Problems;