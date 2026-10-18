import { useState, useRef } from 'react';
import { analyzePhoto } from '../api/client';
import './Identify.css';

const MAX_BYTES = 8 * 1024 * 1024;
const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp'];

function Identify() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const reset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFileChange = (e) => {
    const chosen = e.target.files?.[0];
    if (!chosen) return;

    setError(null);
    setResult(null);

    if (!ACCEPTED.includes(chosen.type)) {
      setError('Please choose a JPEG, PNG, or WebP photo.');
      return;
    }
    if (chosen.size > MAX_BYTES) {
      setError('Photo is larger than 8 MB. Please choose a smaller image.');
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(chosen);
    setPreviewUrl(URL.createObjectURL(chosen));
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzePhoto(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis;
  const metadata = result?.metadata;

  const confidenceColor = {
    high: '#2d6a4f',
    medium: '#b08900',
    low: '#9b2226',
  };

  return (
    <div className="identify-page">
      <header className="identify-header">
        <h1>Identify a plant</h1>
        <p className="identify-sub">
          Upload a photo (or take one with your camera on mobile) to identify
          the plant and check visible symptoms.
        </p>
      </header>

      <section className="upload-panel" aria-label="Photo upload">
        <input
          ref={fileInputRef}
          id="plant-photo"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={handleFileChange}
          className="visually-hidden"
        />
        <label htmlFor="plant-photo" className="upload-label">
          {previewUrl ? 'Choose a different photo' : 'Choose photo or take one'}
        </label>

        {previewUrl && (
          <div className="preview-wrap">
            <img src={previewUrl} alt="Selected plant photo preview" />
            <p className="preview-meta">
              {file.name} · {(file.size / 1024).toFixed(0)} KB
            </p>
          </div>
        )}

        <div className="upload-actions">
          <button
            type="button"
            className="primary-button"
            onClick={handleAnalyze}
            disabled={!file || loading}
          >
            {loading ? 'Analyzing…' : 'Analyze photo'}
          </button>
          {(file || result) && (
            <button type="button" className="small-button" onClick={reset} disabled={loading}>
              Reset
            </button>
          )}
        </div>

        {loading && (
          <p className="identify-status" role="status">
            Asking the AI model… this can take up to a minute.
          </p>
        )}
        {error && (
          <div className="state-message state-error" role="alert">
            {error}
          </div>
        )}
      </section>

      {analysis && (
        <div className="analysis-results">
          <section className="analysis-card identification-card">
            <h2>Identification</h2>
            <p className="identified-name">{analysis.identification.likely_name}</p>
            <p
              className="confidence-badge"
              style={{ background: confidenceColor[analysis.identification.confidence] || '#52796f' }}
            >
              {analysis.identification.confidence} confidence
            </p>
            <p className="confidence-reasoning">{analysis.identification.confidence_reasoning}</p>
            {analysis.identification.possible_species?.length > 0 && (
              <>
                <h3>Possible species</h3>
                <ul>
                  {analysis.identification.possible_species.map((species) => (
                    <li key={species}>{species}</li>
                  ))}
                </ul>
              </>
            )}
            {analysis.identification.visible_characteristics?.length > 0 && (
              <>
                <h3>Visible characteristics</h3>
                <ul>
                  {analysis.identification.visible_characteristics.map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              </>
            )}
          </section>

          {analysis.observations?.length > 0 && (
            <section className="analysis-card">
              <h2>Observations</h2>
              <ul className="observation-list">
                {analysis.observations.map((obs, i) => (
                  <li key={`${obs.observation}-${i}`}>
                    <span className={`severity severity-${obs.severity}`}>{obs.severity}</span>
                    {obs.observation}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {analysis.possible_causes?.length > 0 && (
            <section className="analysis-card">
              <h2>Possible causes</h2>
              <ul>
                {analysis.possible_causes.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </section>
          )}

          {analysis.care_recommendations?.length > 0 && (
            <section className="analysis-card">
              <h2>Care recommendations</h2>
              <ul>
                {analysis.care_recommendations.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </section>
          )}

          {analysis.follow_up_observations?.length > 0 && (
            <section className="analysis-card">
              <h2>Watch for next</h2>
              <ul>
                {analysis.follow_up_observations.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            </section>
          )}

          <p className="analysis-disclaimer" role="note">
            {analysis.disclaimer}
          </p>

          {metadata && (
            <p className="analysis-meta">
              Model: {metadata.model} ·{' '}
              {(metadata.processing_time_seconds ?? 0).toFixed(1)}s ·{' '}
              {analysis.source === 'mock' ? 'demo result (mock AI)' : 'AI-generated result'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default Identify;
