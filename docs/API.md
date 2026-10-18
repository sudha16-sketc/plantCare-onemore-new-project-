# API Reference

Base URL (local dev): `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs` (Swagger UI)

All responses are JSON. Errors use a consistent shape:

```json
{ "success": false, "error": "machine_code", "detail": "human readable message" }
```

Authentication uses **Bearer JWT** (`Authorization: Bearer <token>`).
Tokens are obtained from `/api/v1/auth/register` or `/api/v1/auth/login`.

Rate limits:
- AI endpoints (`/generate-plant-guide`, `/api/v1/analyze/photo`) are
  limited per client IP (`AI_RATE_LIMIT_REQUESTS` per
  `AI_RATE_LIMIT_WINDOW_SECONDS`, default 10/min).
- Auth endpoints (`/api/v1/auth/register`, `/api/v1/auth/login`) share a
  per-IP cap (`AUTH_RATE_LIMIT_REQUESTS` per `AUTH_RATE_LIMIT_WINDOW_SECONDS`,
  default 20/min), and `login` additionally enforces a per-account lockout
  after `LOGIN_MAX_FAILURES` failures (default 5) within
  `LOGIN_FAILURE_WINDOW_SECONDS` (default 300s) — keyed by the submitted
  email whether or not the account exists, so the lockout never reveals
  account existence.

All rate-limited responses are **429** with the same generic body
(`code: "rate_limited"`). Read endpoints are never rate-limited by this
limiter.

---

## System

### `GET /health` — liveness
```json
{ "status": "healthy", "version": "1.1.0" }
```

### `GET /ready` — readiness (honest reporting)
```json
{
  "ready": true,
  "storage_mode": "mongodb",
  "storage_ok": true,
  "ai_configured": true,
  "mock_ai_allowed": false,
  "version": "1.1.0"
}
```
- `storage_mode`: `"mongodb"` or `"memory"`.
- `storage_ok`: actual connectivity probe result for MongoDB.
- `ai_configured`: whether a Gemini key is present and usable.
- `mock_ai_allowed`: mirrors `ALLOW_MOCK_AI` (should be `false` in production).

---

## Auth (`/api/v1/auth`)

### `POST /api/v1/auth/register` — create account → **201**
```json
{ "email": "you@example.com", "username": "you", "password": "min-8-chars" }
```
Response:
```json
{ "access_token": "<jwt>", "token_type": "bearer", "user": { "id": "…", "email": "…", "username": "…", "created_at": "…" } }
```
Errors: **409** email already registered; **422** validation.

### `POST /api/v1/auth/login` — sign in
```json
{ "email": "you@example.com", "password": "…" }
```
Same response shape as register. Errors: **401** bad credentials.

### `GET /api/v1/auth/me` — current user (auth required)
```json
{ "id": "…", "email": "…", "username": "…", "created_at": "…" }
```
Errors: **401** missing/invalid/expired token.

### `PATCH /api/v1/auth/me` — update profile (auth required)
```json
{ "username": "newname", "email": "new@example.com" }
```
Both fields optional. Password changes are not supported via this endpoint.

---

## Care guide

### `POST /generate-plant-guide` — AI care guide + PPTX
No auth required (rate-limited).

Request:
```json
{
  "plant_name": "Tomato",
  "plant_type": "Vegetable",
  "climate": "Temperate",
  "sunlight_hours": 6,
  "soil_type": "Loamy",
  "watering_frequency": "Weekly",
  "experience_level": "Beginner"
}
```
Response (abbreviated):
```json
{
  "success": true,
  "plant_care_guidance": {
    "plant_overview": { "description": "…", "ideal_conditions": {}, "benefits": [], "difficulty_level": "Beginner" },
    "growth_stages": [ { "stage_name": "…", "duration": "…", "care_instructions": "…", "key_indicators": [] } ],
    "daily_care": { "morning_routine": [], "afternoon_routine": [], "evening_routine": [], "weekly_tasks": [] },
    "common_problems": [ { "problem": "…", "symptoms": [], "solution": "…", "prevention": "…" } ],
    "additional_tips": []
  },
  "visual_guide": {
    "status": "success",
    "file_url": "http://localhost:8000/api/v1/files/tomato_care_guide_ab12cd34.pptx",
    "file_type": "pptx",
    "message": "Care guide presentation generated successfully"
  },
  "metadata": { "ai_source": "gemini", "timestamp": "…", "processing_time_seconds": 2.5 }
}
```
Errors:
- **503** AI unavailable (no `GEMINI_API_KEY` and `ALLOW_MOCK_AI=false`).
- **429** rate limited.
- With `ALLOW_MOCK_AI=true`, `metadata.ai_source` is `"mock"` — clients must label it as demo output.

---

## Photo analysis

### `POST /api/v1/analyze/photo` — identify plant + visible symptoms (rate-limited)
`multipart/form-data`, field `file`, max 8 MB.
Accepted types: `image/jpeg`, `image/png`, `image/webp`.

Response (abbreviated):
```json
{
  "success": true,
  "analysis": {
    "identification": {
      "likely_name": "Azalea",
      "possible_species": ["Rhododendron simsii"],
      "confidence": "medium",
      "confidence_reasoning": "…",
      "visible_characteristics": ["…"]
    },
    "observations": [ { "observation": "…", "severity": "mild" } ],
    "possible_causes": ["…"],
    "care_recommendations": ["…"],
    "follow_up_observations": ["…"],
    "disclaimer": "Educational guidance only…",
    "source": "gemini"
  },
  "metadata": { "model": "…", "image_mime_type": "image/png", "image_bytes": 1234, "processing_time_seconds": 14.2 }
}
```
Errors: **415** wrong content type; **400** content-type lies about the
actual bytes (magic-number check); **413** too large; **429** rate limited;
**503** AI unavailable.

---

## Plant collection (`/api/v1/plants`) — auth required

All endpoints operate on the **token's** user only; ids belonging to other
users return **404** (not 403 — existence isn't leaked).

### `GET /api/v1/plants` → `200`
Array of summaries:
```json
[{ "id": "…", "name": "Basil", "species": "Ocimum basilicum", "location": null,
   "watering_interval_days": 7, "reminder_enabled": true,
   "last_watered_at": null, "next_watering_at": "…", "photo_path": null,
   "created_at": "…" }]
```

### `POST /api/v1/plants` → **201**
```json
{
  "name": "Basil",
  "species": "Ocimum basilicum",
  "location": "Kitchen sill",
  "sunlight": "6 hours",
  "soil_type": "Loamy",
  "climate": "Temperate",
  "care_notes": "…",
  "watering_interval_days": 7,
  "reminder_enabled": true
}
```
Only `name` is required. `watering_interval_days` must be 1–365.
`next_watering_at` is computed from `watering_interval_days`.

### `GET /api/v1/plants/{id}` → `200` — full record incl. watering history
### `PATCH /api/v1/plants/{id}` → `200` — partial update (same fields as create, all optional)
### `DELETE /api/v1/plants/{id}` → **204**

### `POST /api/v1/plants/{id}/waterings` → `200`
```json
{ "notes": "deep watering" }   // notes optional, ≤500 chars
```
Records the event, sets `last_watered_at`, and advances `next_watering_at`
by the plant's interval. Returns the updated plant record.

### `GET /api/v1/plants/{id}/waterings` → `200`
Array of `{ id, plant_id, user_id, watered_at, notes }`.

### `PATCH /api/v1/plants/{id}/reminder` → `200`
```json
{ "reminder_enabled": false, "watering_interval_days": 7 }
```
`watering_interval_days` optional.

### `POST /api/v1/plants/{id}/postpone` → `200`
```json
{ "days": 1 }    // 1–30
```
Pushes `next_watering_at` forward without recording a watering.

---

## Files

### `GET /api/v1/files/{file_name}` — download a generated presentation
Only files inside the generated-files directory are served; names are
slug-checked and traversal (`..`, slashes) returns **404**. Responses use
`Content-Disposition: attachment`.

---

## Status code summary

| Code | Meaning |
|------|---------|
| 200/201/204 | OK / created / no content |
| 400 | Bad input (e.g. file bytes don't match declared type) |
| 401 | Missing/invalid credentials or token |
| 404 | Not found (including other users' plants) |
| 409 | Conflict (email already registered) |
| 413 | Upload too large |
| 415 | Unsupported media type |
| 422 | Pydantic validation failure |
| 429 | AI endpoint rate limit exceeded |
| 503 | AI service unavailable (and mock disabled) |
