import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import * as api from '../api/client';
import './MyPlants.css';

const INTERVAL_OPTIONS = [
  { label: 'Daily', days: 1 },
  { label: 'Every 2–3 days', days: 3 },
  { label: 'Weekly', days: 7 },
  { label: 'Bi-weekly', days: 14 },
  { label: 'Monthly', days: 30 },
];

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString() : '—';
}

function isOverdue(plant) {
  return (
    plant.reminder_enabled &&
    plant.next_watering_at &&
    new Date(plant.next_watering_at) <= new Date()
  );
}

function MyPlants() {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const [newPlant, setNewPlant] = useState({
    name: '',
    species: '',
    location: '',
    climate: '',
    soil_type: '',
    sunlight: '',
    watering_interval_days: 7,
    care_notes: '',
  });

  const loadPlants = useCallback(async () => {
    setError(null);
    try {
      const data = await api.listPlants();
      setPlants(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPlants();
  }, [loadPlants]);

  const flash = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(null), 3000);
  };

  const handleWater = async (plant) => {
    try {
      await api.recordWatering(plant.id);
      flash(`Watered ${plant.name} 💧`);
      loadPlants();
    } catch (err) {
      setError(err.message);
    }
  };

  const handlePostpone = async (plant) => {
    try {
      await api.postponeWatering(plant.id, 1);
      flash(`Postponed ${plant.name}'s watering by 1 day`);
      loadPlants();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggleReminder = async (plant) => {
    try {
      await api.updateReminder(plant.id, {
        reminder_enabled: !plant.reminder_enabled,
      });
      flash(
        `Reminder ${plant.reminder_enabled ? 'disabled' : 'enabled'} for ${plant.name}`,
      );
      loadPlants();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (plant) => {
    if (!window.confirm(`Remove ${plant.name} from your collection?`)) return;
    try {
      await api.deletePlant(plant.id);
      flash(`Removed ${plant.name}`);
      loadPlants();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.createPlant({
        ...newPlant,
        species: newPlant.species || null,
        location: newPlant.location || null,
        climate: newPlant.climate || null,
        soil_type: newPlant.soil_type || null,
        sunlight: newPlant.sunlight || null,
        care_notes: newPlant.care_notes || null,
        watering_interval_days: parseInt(newPlant.watering_interval_days, 10),
      });
      flash(`Added ${newPlant.name} to your collection`);
      setNewPlant({
        name: '',
        species: '',
        location: '',
        climate: '',
        soil_type: '',
        sunlight: '',
        watering_interval_days: 7,
        care_notes: '',
      });
      setShowAddForm(false);
      loadPlants();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleAddChange = (e) => {
    setNewPlant({ ...newPlant, [e.target.name]: e.target.value });
  };

  return (
    <div className="my-plants-page">
      <header className="my-plants-header">
        <div>
          <h1>My Plants</h1>
          <p className="my-plants-sub">
            Track your collection, watering history, and reminders.
          </p>
        </div>
        <button
          type="button"
          className="primary-button"
          onClick={() => setShowAddForm(!showAddForm)}
          aria-expanded={showAddForm}
        >
          {showAddForm ? 'Close' : '+ Add plant'}
        </button>
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

      {showAddForm && (
        <form className="add-plant-form" onSubmit={handleAddSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="plant-name">Name *</label>
              <input
                id="plant-name"
                name="name"
                type="text"
                value={newPlant.name}
                onChange={handleAddChange}
                required
                maxLength={100}
                placeholder="e.g. Kitchen Basil"
              />
            </div>
            <div className="form-group">
              <label htmlFor="plant-species">Species</label>
              <input
                id="plant-species"
                name="species"
                type="text"
                value={newPlant.species}
                onChange={handleAddChange}
                maxLength={120}
                placeholder="e.g. Ocimum basilicum"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="plant-location">Location</label>
              <input
                id="plant-location"
                name="location"
                type="text"
                value={newPlant.location}
                onChange={handleAddChange}
                maxLength={120}
                placeholder="e.g. South-facing windowsill"
              />
            </div>
            <div className="form-group">
              <label htmlFor="plant-interval">Water every</label>
              <select
                id="plant-interval"
                name="watering_interval_days"
                value={newPlant.watering_interval_days}
                onChange={handleAddChange}
              >
                {INTERVAL_OPTIONS.map((opt) => (
                  <option key={opt.days} value={opt.days}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="plant-climate">Climate</label>
              <input
                id="plant-climate"
                name="climate"
                type="text"
                value={newPlant.climate}
                onChange={handleAddChange}
                maxLength={60}
                placeholder="e.g. Temperate"
              />
            </div>
            <div className="form-group">
              <label htmlFor="plant-soil">Soil type</label>
              <input
                id="plant-soil"
                name="soil_type"
                type="text"
                value={newPlant.soil_type}
                onChange={handleAddChange}
                maxLength={60}
                placeholder="e.g. Loamy"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="plant-notes">Care notes</label>
            <textarea
              id="plant-notes"
              name="care_notes"
              value={newPlant.care_notes}
              onChange={handleAddChange}
              maxLength={2000}
              rows={3}
              placeholder="Anything special about this plant…"
            />
          </div>

          <button type="submit" className="primary-button" disabled={saving}>
            {saving ? 'Saving…' : 'Save plant'}
          </button>
        </form>
      )}

      {loading && <p className="state-message">Loading your plants…</p>}

      {!loading && plants.length === 0 && (
        <div className="state-message state-empty">
          <p>No plants yet. Add one above, or generate a care guide from the home page.</p>
          <Link to="/" className="state-link">
            Generate a care guide →
          </Link>
        </div>
      )}

      {!loading && plants.length > 0 && (
        <ul className="plant-list">
          {plants.map((plant) => {
            const overdue = isOverdue(plant);
            return (
              <li key={plant.id} className={`plant-card ${overdue ? 'overdue' : ''}`}>
                <div className="plant-card-main">
                  <Link to={`/plants/${plant.id}`} className="plant-card-name">
                    {plant.name}
                  </Link>
                  {plant.species && <span className="plant-card-species">{plant.species}</span>}
                  {overdue && <span className="overdue-badge">Needs water</span>}
                </div>

                <dl className="plant-card-meta">
                  <div>
                    <dt>Last watered</dt>
                    <dd>{formatDate(plant.last_watered_at)}</dd>
                  </div>
                  <div>
                    <dt>Next watering</dt>
                    <dd>{formatDate(plant.next_watering_at)}</dd>
                  </div>
                  <div>
                    <dt>Interval</dt>
                    <dd>Every {plant.watering_interval_days} days</dd>
                  </div>
                </dl>

                <div className="plant-card-actions">
                  <button
                    type="button"
                    className="small-button water-button"
                    onClick={() => handleWater(plant)}
                  >
                    Watered
                  </button>
                  {overdue && (
                    <button
                      type="button"
                      className="small-button"
                      onClick={() => handlePostpone(plant)}
                    >
                      Postpone 1 day
                    </button>
                  )}
                  <button
                    type="button"
                    className="small-button"
                    onClick={() => handleToggleReminder(plant)}
                  >
                    {plant.reminder_enabled ? 'Mute reminder' : 'Enable reminder'}
                  </button>
                  <button
                    type="button"
                    className="small-button danger-button"
                    onClick={() => handleDelete(plant)}
                  >
                    Remove
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default MyPlants;
