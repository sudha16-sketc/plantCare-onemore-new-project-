# Architecture

## System overview

```
┌──────────────┐      ┌──────────────┐      ┌─────────────────────────────┐
│  Web (React) │      │ Mobile (Expo│      │        FastAPI backend      │
│  Vite build  │      │  RN / Hermes)│      │                             │
└──────┬───────┘      └──────┬───────┘      │  routes → services → store  │
       │  fetch + JWT        │  fetch+JWT   │                             │
       └─────────────────────┴─────────────►│  ┌─────────┐  ┌──────────┐  │
                                            │  │ Gemini  │  │ MongoDB  │  │
                                            │  │ (AI)    │  │ or memory│  │
                                            │  └─────────┘  └──────────┘  │
                                            │  ppt_service → generated/   │
                                            └─────────────────────────────┘
```

Both clients share one API contract (`docs/API.md`) and near-identical
API-client code: JWT bearer token in `localStorage` (web) or
`AsyncStorage` (mobile), JSON errors normalized to a single `ApiError`
shape, and FormData uploads for photos.

## Backend layers

```
routes/      HTTP concerns: validation, status codes, auth dependencies
  ↓
services/    business logic: gemini.py (AI), ppt_service.py (PPTX files)
  ↓
db/          storage abstraction: BaseStore → MongoStore | MemoryStore
```

### Request lifecycle (example: care-guide generation)

1. `POST /generate-plant-guide` hits `routes/guide.py`.
2. `enforce_ai_rate_limit(request)` — sliding in-memory window per client IP
   (never applied to reads; only to AI endpoints).
3. `PlantInputData` (Pydantic) validates length/option constraints.
4. `GeminiService.generate_plant_guide()` calls the official `google-genai`
   SDK. The API key never appears in URLs or client payloads. If the key is
   missing: 503 with a clear message — unless `ALLOW_MOCK_AI=true`, in
   which case the mock is returned with `ai_source: "mock"` end-to-end.
5. `ppt_service` renders a `.pptx` into the configured generated-files
   directory using a slugified, random-suffixed filename; old files are
   garbage-collected by TTL.
6. Response carries an **absolute** `file_url`
   (`/api/v1/files/{name}`), which a dedicated safe-path route serves.

### Auth flow

- Register/login verify with bcrypt (`bcrypt.gensalt(rounds=12)`),
  issue a JWT (`HS256`, expiry from config) containing only the user id.
- Every authenticated request resolves identity via
  `get_current_user` → token → user record. Request bodies containing
  `user_id` are ignored for authorization purposes; the collection routes
  filter every query by the token's user id, which is what provides
  cross-user isolation (covered by tests).

### Storage abstraction

`app/db/store.py` defines `BaseStore` (users + plants + waterings).
Startup picks an implementation:

- `MONGODB_URI` set → `MongoStore` (indexes on user id + plant ownership);
- otherwise → `MemoryStore` (dicts; fine for dev, data dies with the process).

`/ready` reports the **actual** mode and connectivity
(`storage_mode`, `storage_ok`) — a failed Mongo connection never silently
degrades to pretending everything is fine.

### Error handling

`app/core/errors.py` defines an `AppError` hierarchy mapped to consistent
JSON: `{"success": false, "error": code, "detail": human string}`.
Unhandled exceptions are logged server-side and returned as a generic 500 —
stack traces and internal paths never reach clients when `DEBUG=false`.

## Web frontend

- Single API client (`src/api/client.js`) — token injection, network-error
  messaging, upload pre-validation.
- `AuthContext` restores the session from a stored JWT via
  `GET /api/v1/auth/me` on load; expired tokens are cleared silently.
- Pages: Home (guide form + results), Dashboard (overdue/upcoming
  waterings), My Plants (CRUD/water/postpone/reminders), Plant Detail
  (history + notes), Identify (photo analysis), Login, Profile.
- The three.js hero canvas is replaced by a static gradient when the user
  prefers reduced motion; a global CSS rule also neutralizes animations.
- Vite `manualChunks` keeps three.js (~1.1 MB) out of the app chunk (~58 KB),
  so non-3D pages don't pay for the hero.

## Mobile (Expo)

Mirrors the web feature set with the same API client semantics:
- Screens: Guide, Identify, Plants, PlantDetail, Profile, Login.
- Token in AsyncStorage; photo capture via `expo-image-picker`
  (permission strings declared in `app.json`).
- Base URL: `EXPO_PUBLIC_API_URL` (EAS profile env) → `app.json extra` →
  `10.0.2.2:8000` (Android emulator) / `localhost:8000`.
- Builds: `eas build --platform android|ios` (local Android SDK not
  required; `expo export` Hermes bundles verified for both platforms).

## Configuration

All backend config lives in `app/utils/config.py` (pydantic-settings),
loaded once at import from env / `backend/.env`. Clients read only
`VITE_API_URL` / `EXPO_PUBLIC_API_URL` — no secrets are ever shipped to
either frontend.
