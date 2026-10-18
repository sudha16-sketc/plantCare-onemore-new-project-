import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import * as api from '../api/client';
import './Dashboard.css';

function Dashboard() {
  const { user } = useAuth();
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.listPlants();
        if (!cancelled) setPlants(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const now = new Date();
  const needsWater = plants.filter(
    (p) => p.reminder_enabled && p.next_watering_at && new Date(p.next_watering_at) <= now,
  );
  const upcoming = plants
    .filter((p) => p.next_watering_at && new Date(p.next_watering_at) > now)
    .sort((a, b) => new Date(a.next_watering_at) - new Date(b.next_watering_at))
    .slice(0, 3);

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>
          {user ? `Hello, ${user.username}` : 'Your Plant Dashboard'}
        </h1>
        <p className="dashboard-sub">
          Quick overview of your plants and watering schedule.
        </p>
      </header>

      <div className="dashboard-actions">
        <Link to="/identify" className="action-card">
          <span className="action-icon" aria-hidden="true">📷</span>
          <h2>Identify a plant</h2>
          <p>Upload or take a photo to identify a plant and check visible symptoms.</p>
        </Link>
        <Link to="/" className="action-card">
          <span className="action-icon" aria-hidden="true">✨</span>
          <h2>Care guide</h2>
          <p>Generate a detailed AI care guide with growth stages and routines.</p>
        </Link>
        <Link to="/plants" className="action-card">
          <span className="action-icon" aria-hidden="true">🪴</span>
          <h2>My plants</h2>
          <p>Manage your collection, watering history, and reminders.</p>
        </Link>
      </div>

      {loading && <p className="state-message">Loading your plants…</p>}
      {error && (
        <div className="state-message state-error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && plants.length === 0 && (
        <div className="state-message state-empty">
          <p>You haven&apos;t added any plants yet.</p>
          <Link to="/identify" className="state-link">
            Identify your first plant →
          </Link>
        </div>
      )}

      {!loading && needsWater.length > 0 && (
        <section className="dashboard-section" aria-labelledby="needs-water-heading">
          <h2 id="needs-water-heading">💧 Needs water now</h2>
          <ul className="plant-strip">
            {needsWater.map((p) => (
              <li key={p.id}>
                <Link to={`/plants/${p.id}`} className="plant-chip overdue">
                  {p.name}
                  <span className="chip-meta">
                    due {new Date(p.next_watering_at).toLocaleDateString()}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {!loading && upcoming.length > 0 && (
        <section className="dashboard-section" aria-labelledby="upcoming-heading">
          <h2 id="upcoming-heading">Upcoming waterings</h2>
          <ul className="plant-strip">
            {upcoming.map((p) => (
              <li key={p.id}>
                <Link to={`/plants/${p.id}`} className="plant-chip">
                  {p.name}
                  <span className="chip-meta">
                    {new Date(p.next_watering_at).toLocaleDateString()}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default Dashboard;
