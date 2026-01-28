// src/components/ExtraTips.jsx
export default function ExtraTips({ tips }) {
  if (!tips || tips.length === 0) return null;

  // Ensure tips is an array
  const tipsList = Array.isArray(tips) ? tips : (typeof tips === 'string' ? tips.split('\n').filter(t => t.trim()) : []);

  if (tipsList.length === 0) return null;

  return (
    <div style={{ margin: '20px 0' }}>
      <h3>💡 Extra Tips</h3>
      <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
        {tipsList.map((tip, index) => (
          <li key={index} style={{ marginBottom: '5px' }}>
            {tip}
          </li>
        ))}
      </ul>
    </div>
  );
}
