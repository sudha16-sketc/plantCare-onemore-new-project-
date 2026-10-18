/**
 * PlantCare API client.
 *
 * All backend calls go through here so auth headers, base URL, and error
 * normalization stay consistent. Configure VITE_API_URL at build time
 * (defaults to http://localhost:8000 for local development).
 */

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const TOKEN_KEY = 'plantcare_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(message, status, code) {
    super(message);
    this.status = status;
    this.code = code || 'error';
  }
}

async function request(path, { method = 'GET', body, headers = {}, isFormData = false } = {}) {
  const finalHeaders = { ...headers };
  const token = getToken();
  if (token) finalHeaders.Authorization = `Bearer ${token}`;
  if (body && !isFormData) finalHeaders['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: finalHeaders,
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(
      'Unable to reach the server. Check your connection and that the backend is running.',
      0,
      'network_error',
    );
  }

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    /* non-JSON response */
  }

  if (!response.ok) {
    const message =
      (data && (data.error || data.detail)) ||
      `Request failed (${response.status})`;
    throw new ApiError(message, response.status, data?.code);
  }
  return data;
}

/* ---------------- Auth ---------------- */

export async function register(email, username, password) {
  const data = await request('/api/v1/auth/register', {
    method: 'POST',
    body: { email, username, password },
  });
  setToken(data.access_token);
  return data.user;
}

export async function login(email, password) {
  const data = await request('/api/v1/auth/login', {
    method: 'POST',
    body: { email, password },
  });
  setToken(data.access_token);
  return data.user;
}

export async function fetchMe() {
  return request('/api/v1/auth/me');
}

export async function updateMe(fields) {
  return request('/api/v1/auth/me', { method: 'PATCH', body: fields });
}

/* ---------------- Plant guide ---------------- */

export async function generatePlantGuide(formData) {
  const payload = {
    plant_name: formData.plant_name,
    plant_type: formData.plant_type,
    climate: formData.climate,
    sunlight_hours: parseInt(formData.sunlight_hours, 10),
    soil_type: formData.soil_type,
    watering_frequency: formData.watering_frequency,
    experience_level: formData.experience_level,
  };
  return request('/generate-plant-guide', { method: 'POST', body: payload });
}

/* ---------------- Photo analysis ---------------- */

export async function analyzePhoto(file) {
  if (!file) throw new ApiError('No photo selected.', 0, 'no_file');
  const allowed = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowed.includes(file.type)) {
    throw new ApiError('Please choose a JPEG, PNG, or WebP photo.', 415, 'unsupported_media_type');
  }
  const maxBytes = 8 * 1024 * 1024;
  if (file.size > maxBytes) {
    throw new ApiError('Photo is larger than 8 MB. Please choose a smaller image.', 413, 'image_too_large');
  }
  const body = new FormData();
  body.append('file', file);
  return request('/api/v1/analyze/photo', { method: 'POST', body, isFormData: true });
}

/* ---------------- Plant collection ---------------- */

export async function listPlants() {
  return request('/api/v1/plants');
}

export async function getPlant(id) {
  return request(`/api/v1/plants/${id}`);
}

export async function createPlant(data) {
  return request('/api/v1/plants', { method: 'POST', body: data });
}

export async function updatePlant(id, data) {
  return request(`/api/v1/plants/${id}`, { method: 'PATCH', body: data });
}

export async function deletePlant(id) {
  return request(`/api/v1/plants/${id}`, { method: 'DELETE' });
}

export async function recordWatering(id, notes) {
  return request(`/api/v1/plants/${id}/waterings`, {
    method: 'POST',
    body: notes ? { notes } : {},
  });
}

export async function wateringHistory(id) {
  return request(`/api/v1/plants/${id}/waterings`);
}

export async function updateReminder(id, data) {
  return request(`/api/v1/plants/${id}/reminder`, { method: 'PATCH', body: data });
}

export async function postponeWatering(id, days) {
  return request(`/api/v1/plants/${id}/postpone`, { method: 'POST', body: { days } });
}

/* ---------------- Misc ---------------- */

export async function fetchHealth() {
  return request('/health');
}

export { API_BASE_URL };
