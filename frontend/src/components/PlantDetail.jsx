import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import * as api from '../api/client';
import './PlantDetail.css';

function formatDate(value) {
  return value
    ? new Date(value).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : '—';
}

function PlantDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [plant, setPlant] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [plantData, historyData] = await Promise.all([
        api.getPlant(id),
        api.wateringHistory(id),
      ]);
      setPlant(plantData);
      setHistory(historyData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const flash = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(null), 3000);
  };

  const handleWater = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.recordWatering(id, notes.trim() || undefined);
      setNotes('');
      flash('Watering recorded 💧');
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handlePostpone = async () => {
    try {
      await api.postponeWatering(id, 1);
      flash('Watering postponed by 1 day');
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggleReminder = async () => {
    try {
      await api.updateReminder(id, { reminder_enabled: !plant.reminder_enabled });
      flash(`Reminder ${plant.reminder_enabled ? 'disabled' : 'enabled'}`);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Remove ${plant.name} from your collection?`)) return;
    try {
      await api.deletePlant(id);
      navigate('/plants');
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p className="state-message">Loading plant…</p>;

  if (error && !plant) {
    return (
      <div className="plant-detail-page">
        <div className="state-message state-error" role="alert">
          {error}
        </div>
        <Link to="/plants" className="state-link">
          ← Back to my plants
        </Link>
      </div>
    );
  }

  const overdue =
    plant.reminder_enabled &&
    plant.next_watering_at &&
    new Date(plant.next_watering_at) <= new Date();

  return (
    <div className="plant-detail-page">
      <Link to="/plants" className="back-link">
        ← Back to my plants
      </Link>

      <header className="detail-header">
        <div>
          <h1>
            {plant.name}
            {overdue && <span className="overdue-badge">Needs water</span>}
          </h1>
          {plant.species && <p className="detail-species">{plant.species}</p>}
        </div>
        <div className="detail-header-actions">
          <button type="button" className="small-button" onClick={handleToggleReminder}>
            {plant.reminder_enabled ? 'Mute reminder' : 'Enable reminder'}
          </button>
          <button type="button" className="small-button danger-button" onClick={handleDelete}>
            Remove plant
          </button>
        </div>
      </header>

      {notice && (
        <div className="state-message" role="status">
          {notice}
        </div>
      )}
      {error && (
        <div className="state-message state-error" role="alert">
          {error}
        </div>
      )}

      <section className="detail-grid" aria-label="Plant details">
        <div className="detail-card">
          <h2>Details</h2>
          <dl>
            <div>
              <dt>Location</dt>
              <dd>{plant.location || '—'}</dd>
            </div>
            <div>
              <dt>Climate</dt>
              <dd>{plant.climate || '—'}</dd>
            </div>
            <div>
              <dt>Soil</dt>
              <dd>{plant.soil_type || '—'}</dd>
            </div>
            <div>
              <dt>Sunlight</dt>
              <dd>{plant.sunlight || '—'}</dd>
            </div>
            <div>
              <dt>Watering interval</dt>
              <dd>Every {plant.watering_interval_days} days</dd>
            </div>
            <div>
              <dt>Last watered</dt>
              <dd>{formatDate(plant.last_watered_at)}</dd>
            </div>
            <div>
              <dt>Next watering</dt>
              <dd>{formatDate(plant.next_watering_at)}</dd>
            </div>
          </dl>
          {plant.care_notes && (
            <>
              <h3>Care notes</h3>
              <p className="care-notes">{plant.care_notes}</p>
            </>
          )}
        </div>

        <div className="detail-card">
          <h2>Record a watering</h2>
          <form onSubmit={handleWater} className="water-form">
            <label htmlFor="water-notes">Notes (optional)</label>
            <textarea
              id="water-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={500}
              rows={3}
              placeholder="e.g. Deep watering, drained saucer"
            />
            <div className="water-form-actions">
              <button type="submit" className="primary-button" disabled={saving}>
                {saving ? 'Saving…' : 'I watered this plant'}
              </button>
              <button type="button" className="small-button" onClick={handlePostpone}>
                Postpone 1 day
              </button>
            </div>
          </form>

          <h2>Watering history</h2>
          {history.length === 0 ? (
            <p className="history-empty">No waterings recorded yet.</p>
          ) : (
            <ul className="history-list">
              {history.map((event) => (
                <li key={event.id}>
                  <time dateTime={event.watered_at}>{formatDate(event.watered_at)}</time>
                  {event.notes && <span className="history-notes">{event.notes}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}

export default PlantDetail;
