import './DailyCare.css';

const DailyCare = ({ care }) => {
  if (!care) return null;

  // Handle both string and array formats
  const parseRoutine = (routine) => {
    if (!routine) return [];
    if (typeof routine === 'string') {
      return routine.split('\n').filter(item => item.trim());
    }
    return Array.isArray(routine) ? routine : [];
  };

  const timeSlots = [
    { key: 'morning', label: 'Morning', icon: '🌅', gradient: 'linear-gradient(135deg, #FFE5B4, #FFD700)' },
    { key: 'afternoon', label: 'Afternoon', icon: '☀️', gradient: 'linear-gradient(135deg, #87CEEB, #4682B4)' },
    { key: 'evening', label: 'Evening', icon: '🌙', gradient: 'linear-gradient(135deg, #9370DB, #483D8B)' }
  ];

  return (
    <div className="daily-care">
      <h2 className="care-title">Daily Care Routine</h2>
      <p className="care-subtitle">Follow this schedule to keep your plant thriving</p>

      <div className="routine-grid">
        {timeSlots.map((slot, index) => {
          const routineKey = slot.key === 'morning' ? 'morning' : slot.key === 'afternoon' ? 'afternoon' : 'evening';
          const routineData = care[routineKey];
          
          return (
            routineData && (
              <div 
                key={slot.key} 
                className="routine-card"
                style={{ animationDelay: `${index * 0.15}s` }}
              >
                <div className="routine-header" style={{ background: slot.gradient }}>
                  <span className="routine-icon">{slot.icon}</span>
                  <h3 className="routine-time">{slot.label}</h3>
                </div>
                <div className="routine-content">
                  <p className="routine-text">{routineData}</p>
                </div>
              </div>
            )
          );
        })}
      </div>

      {care.weekly_tasks && care.weekly_tasks.length > 0 && (
        <div className="weekly-section">
          <h3 className="weekly-title">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
              <path d="M16 2V6M8 2V6M3 10H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Weekly Tasks
          </h3>
          <div className="weekly-tasks">
            {care.weekly_tasks.map((task, index) => (
              <div key={index} className="task-item">
                <div className="task-checkbox">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 13L9 17L19 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <span className="task-text">{task}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyCare;