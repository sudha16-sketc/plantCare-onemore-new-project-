# PlantCare — Implementation Plan

**Date:** 2026-10-18
**Branch:** `feature/plantcare-web-mobile`
**Auditor:** Automated full-stack audit against the actual repository state

---

## 1. Current architecture (verified)

```
PlantCare/
├── backend/                  FastAPI (Python 3.12)
│   ├── app/main.py           App factory, CORS, /files static mount
│   ├── app/services/plant.py /health, /generate-plant-guide routes
│   ├── app/routes/gemini.py  Gemini REST via httpx (key in query param)
│   ├── app/routes/notebooklm.py  Entirely mock/dead code
│   ├── app/services/ppt_service.py  python-pptx generation → generated_files/
│   ├── app/schemas/plant.py  Pydantic models
│   ├── app/db/mongodb.py     Motor (async Mongo), lazy init
│   ├── .env                  REAL SECRETS (gitignored, never committed)
│   └── generated_files/      Committed .pptx artifacts
└── frontend/                 React 19 + Vite 7
    ├── src/App.jsx           Routes: /, /login, /profile
    ├── src/components/       Hero (Three.js), MainPage, PlantForm, guide views
    └── src/context/AuthContext.jsx  localStorage "auth" with btoa passwords
```

**Verified working:** plant-guide form → backend → Gemini (key present in .env) →
structured guide JSON → guide sections UI → python-pptx generation.

## 2. Audit findings

### Security (must fix)

| # | Severity | Finding |
|---|----------|---------|
| S1 | Critical | `AuthContext.jsx` stores `btoa(password)` (reversible base64) in localStorage and presents it as real login/signup. Must be replaced with backend auth or labeled local-only demo. |
| S2 | High | CORS `allow_origins` contains `"*"` together with `allow_credentials=True` (`main.py:48`). Invalid and insecure. |
| S3 | High | Gemini API key passed as URL query parameter (`gemini.py:123`). Official mechanism is the `x-goog-api-key` header (or official SDK). URLs with keys leak into logs. |
| S4 | High | No authentication/authorization anywhere. Any future per-user data would be unprotected. Client-supplied user IDs would be trusted. |
| S5 | Medium | `generate-plant-guide` leaks internal exception text to clients (`plant.py:153`). |
| S6 | Medium | PPT filename derived from raw `plant_name` (`ppt_service.py:39`) — path traversal possible via names containing `/` or `..`. |
| S7 | Medium | No rate limiting on the expensive AI endpoint; no upload size limits (no upload endpoint exists at all). |
| S8 | Low | Startup banner prints key-configured status; debug prints Gemini response bodies. |

### Correctness / broken features

| # | Finding |
|---|---------|
| B1 | PPT download is broken in the browser: backend returns relative `/files/<name>.pptx`; frontend uses it as `href`, so it resolves against the **frontend** origin (5173) where the file does not exist. |
| B2 | `GeminiService` silently falls back to mock data on **any** error (timeout, quota, malformed JSON) — clients cannot tell mock from real AI (`gemini.py:193-199`). Violates "never silently return mock results". |
| B3 | `plant.py` imports `plant_guides_collection` at module load; when Mongo is unavailable at import time the name stays `None` forever even if Mongo comes up later. |
| B4 | `notebooklm.py` is an entirely mock service against a nonexistent API; UI/docs claim NotebookLM integration. |
| B5 | Dead/unused code: `frontend/src/components/api.js` (superseded by inline fetch in MainPage), `SlideDesign.jsx` (empty component, imported nowhere), `formatter.py` (never called). |
| B6 | No plant identification, no photo upload, no plant collection with watering history, no reminders — product vision requirements not implemented. |
| B7 | `datetime.utcnow()` deprecated; `validator` deprecated in Pydantic v2. |
| B8 | Committed `generated_files/*.pptx` build artifacts and committed `__pycache__` were removed in the last commit, but files regenerate untracked. |
| B9 | `README.md` claims mobile apps "available soon on app stores", Docker deployment, NotebookLM integration — none exist. Misleading docs. |
| B10 | `requirements.txt` unpinned, contains deprecated `fastapi-cors` and duplicate `python-dotenv`. |
| B11 | Settings default `debug=True` (`config.py:32`) — unsafe default. |
| B12 | `/health` never checks Gemini or database; no readiness endpoint. |

### Performance / UX

| # | Finding |
|---|---------|
| U1 | Three.js hero loads a 3D model unconditionally; no `prefers-reduced-motion` or low-end fallback. |
| U2 | No loading/empty/error states for a plant collection (none exists). Guide flow has loading + error states (keep). |
| U3 | No photo upload UI; no camera capture. |

## 3. Target architecture

```
backend/app/
├── main.py                  App + middleware + router registration
├── core/
│   ├── config.py            Settings (env-driven, safe defaults)
│   ├── logging.py           Structured logging (no secrets)
│   ├── security.py          bcrypt hashing, JWT create/verify
│   ├── deps.py              Auth + rate-limit + storage dependencies
│   └── errors.py            Safe error envelopes
├── db/
│   ├── mongodb.py           Motor client (async, health-checked)
│   └── memory.py            In-memory store (dev fallback, labeled in /ready)
├── models/                  Pydantic schemas (renamed from schemas/)
│   ├── plant.py             Guide schemas (existing, cleaned)
│   ├── analysis.py          Photo analysis schemas
│   ├── collection.py        Plant collection + watering schemas
│   └── auth.py              Register/login schemas
├── services/
│   ├── gemini.py            google-genai SDK, header auth, structured output,
│   │                        explicit errors (no silent mock), image analysis
│   ├── ppt_service.py       Sanitized filenames, TTL cleanup, absolute URLs
│   └── analysis.py          Photo validation + orchestration
├── api/
│   ├── health.py            /health, /ready
│   ├── auth.py              /api/v1/auth/register|login|me
│   ├── guide.py             /generate-plant-guide (kept), hardened
│   ├── analysis.py          /api/v1/analyze/photo (multipart)
│   ├── plants.py            CRUD + watering history + reminders (owner-scoped)
│   └── files.py             Controlled /api/v1/files/{slug} download
frontend/src/
├── api/client.js            Fetch wrapper, JWT header, error normalization
├── context/AuthContext.jsx  Backend JWT auth (register/login/logout)
├── pages/                   Home, Login, Dashboard, MyPlants, PlantDetail,
│                            Identify, Guide
└── components/              Existing guide components (kept) + new plant cards,
                             watering controls, upload widget, states
mobile/                      Expo SDK 58 + TypeScript app
docs/                        ARCHITECTURE, API, SECURITY, LOCAL_DEVELOPMENT,
                             ANDROID_BUILD, DEPLOYMENT, TESTING
```

## 4. Phases and acceptance criteria

### Phase 2 — Backend hardening
- Env-driven settings; CORS from env (no `*` with credentials); debug default false.
- bcrypt password hashing; JWT (PyJWT) with expiry; `/api/v1/auth/*`.
- Storage abstraction: MongoDB when `MONGODB_URI` set, else in-memory (explicitly
  reported in `/ready` as `storage: memory` — never pretending to be Mongo).
- Rate limiter (in-process sliding window) on AI endpoints.
- Safe error envelopes; no exception text to clients; no key material in logs.
- Pinned `requirements.txt`; remove `fastapi-cors`, notebooklm mock module.
- **Accept:** pytest suite (mocked Gemini) passes; `uvicorn` starts; auth flow
  works via curl; CORS reflects configured origins only.

### Phase 3 — Photo analysis + guide correctness
- `POST /api/v1/analyze/photo`: multipart, MIME/size validation (jpeg/png/webp,
  ≤ 8 MB), google-genai image input, JSON schema output: identity, confidence
  (explicitly low/medium/high with reasoning), visible characteristics, possible
  symptoms/causes (labeled as observations, not diagnoses), care
  recommendations, follow-up observations.
- Guide generation: real errors on Gemini failure (502/504 with safe message);
  mock data only when `ALLOW_MOCK_AI=true` (dev) and labeled `"source": "mock"`.
- **Accept:** pytest covers valid/invalid uploads, mocked Gemini success,
  provider failure, malformed response.

### Phase 4 — Plants, watering, reminders (API)
- `GET/POST/PATCH/DELETE /api/v1/plants` (owner-scoped from JWT, never from body),
  `POST /api/v1/plants/{id}/waterings`, watering history, `next_watering_at`
  computed from interval, reminder enable/disable + postpone.
- **Accept:** cross-user isolation tests pass (user B cannot read/modify A's plants).

### Phase 5 — PPT + files
- Sanitized slug filenames; `GET /api/v1/files/{slug}` streams with
  `FileResponse` + content-disposition; response returns absolute URL built from
  the request; background cleanup of files older than TTL.
- **Accept:** pytest covers traversal rejection, download 200, cleanup.

### Phase 6-7 — Web frontend
- Backend JWT auth replaces btoa-localStorage; token in localStorage; labeled.
- New pages: Dashboard, My Plants (list/detail/watering), Identify (photo),
  guide view kept. PPT download uses absolute backend URL. Responsive
  breakpoints verified; reduced-motion disables 3D hero.
- **Accept:** `npm run build` + `npm run lint` pass; manual flows verified against
  running backend (guide, register/login, add plant, water, download).

### Phase 8 — Docker
- `backend/Dockerfile` (python:3.12-slim, non-root), `frontend/Dockerfile`
  (multi-stage node→nginx), `compose.yaml` (backend, frontend, mongo),
  `.dockerignore`s, healthchecks.
- **Accept:** `docker-compose config` validates; images build if the local
  container tool permits (podman) — otherwise documented limitation.

### Phase 9 — Expo mobile
- `mobile/` Expo SDK 58 + TypeScript, expo-router navigation, screens:
  onboarding/permissions, home, identify, analysis result, guide, my plants,
  plant detail + water action, watering/reminder settings, settings.
- expo-camera/expo-image-picker with permission flows, image resize, upload;
  expo-notifications local scheduling tied to plant schedules; AsyncStorage for
  session; API base URL configurable (documented emulator host: `10.0.2.2`).
- EAS config (`eas.json`) for preview APK + production AAB. **No claim of a
  completed build** unless `eas build` actually runs (requires Expo account).
- **Accept:** `tsc --noEmit` passes; app boots via `npx expo start` config
  validation; notifications permission-denied path handled.

### Phase 10-11 — Docs, verification, report
- Rewrite README to match reality; full doc set; secret audit; test/build
  results recorded; final report.

## 5. Explicit non-goals
- No Kubernetes/microservices; no forced push; no NotebookLM (no public API —
  removed from claims); no claim of Play Store readiness.

## 6. Known environmental limits (this machine)
- No Java/Android SDK → local Gradle APK build impossible; EAS cloud build
  requires an Expo account token (not available here).
- Podman emulates Docker; builds attempted, limitations documented in DEPLOYMENT.md.
