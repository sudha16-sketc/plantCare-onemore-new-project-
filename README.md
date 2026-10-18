# PlantCare 🌱

AI-powered plant care: generate detailed care guides with Google Gemini,
identify plants from photos, and manage a personal collection with
server-side watering reminders — on web and mobile.

## Features

- **Care guides** — form in, full AI guide out: overview, growth stages,
  morning/afternoon/evening routines, common problems, extra tips, plus a
  downloadable PowerPoint presentation.
- **Photo identification** — upload or photograph a plant to identify it and
  surface visible symptoms, possible causes, care recommendations, and a
  clear "not a substitute for a professional" disclaimer.
- **Plant collection** — signed-in users keep plants on the server:
  watering history, intervals, due dates, reminders, postpone, and
  cross-device sync. Users can only ever touch their own plants.
- **Accounts** — JWT auth with bcrypt-hashed passwords (PyJWT + bcrypt);
  identity always comes from the token, never from the request body.
- **Honest readiness** — `/ready` reports real storage/AI state: it never
  claims success it can't back up, and mock AI output is explicitly labeled.

## Tech stack

| Layer     | Tech |
|-----------|------|
| Backend   | FastAPI, Pydantic v2, Google `google-genai` SDK, python-pptx, PyJWT + bcrypt, Motor/pymongo (MongoDB) with an in-memory fallback store |
| Web       | React 19 + Vite 7, react-router 7, three.js hero background (respects `prefers-reduced-motion`) |
| Mobile    | Expo SDK 58 / React Native 0.88, React Navigation, expo-image-picker |
| Tests     | pytest + httpx ASGI transport (43 tests) |
| Packaging | Docker (backend: python-slim + uvicorn; frontend: node build → nginx SPA), docker-compose |

## Project structure

```
PlantCare/
├── backend/               # FastAPI app
│   ├── app/
│   │   ├── main.py        # App factory, CORS, middleware, error handlers
│   │   ├── core/          # security (JWT/bcrypt), errors, dependencies
│   │   ├── db/            # storage abstraction: MongoStore / MemoryStore
│   │   ├── routes/        # health, auth, guide, analysis, plants, files
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # gemini.py (AI), ppt_service.py (PPTX)
│   │   └── utils/         # config (pydantic-settings)
│   ├── tests/             # pytest suite (43 tests)
│   ├── requirements.txt   # pinned runtime deps
│   └── Dockerfile
├── frontend/              # React web app
│   ├── src/api/client.js  # single API client (JWT, errors, uploads)
│   ├── src/context/       # AuthContext (backend JWT)
│   ├── src/components/    # pages: Dashboard, MyPlants, PlantDetail,
│   │                      #   Identify, Guide (MainPage), Profile, Login
│   └── Dockerfile         # multi-stage → nginx with SPA fallback
├── mobile/                # Expo app (feature parity with web)
│   ├── eas.json           # development / preview / production profiles
│   └── src/               # api client, screens, components, theme
├── docker-compose.yml     # backend :8000 + frontend :3000 (+ optional mongo)
├── docs/                  # architecture, API, security, deployment
└── .env.example keys live in backend/.env.example
```

## Quick start

### Option A — Docker (recommended)

```bash
cp backend/.env.example backend/.env   # then fill in real values
docker-compose up --build
# web:      http://localhost:3000
# api:      http://localhost:8000  (docs at /docs)
# optional MongoDB: docker-compose --profile mongo up --build
```

Without `GEMINI_API_KEY` the API still runs, but AI endpoints return a clear
503 instead of silently faking results. Set `ALLOW_MOCK_AI=true` (dev only)
to exercise the full flow with labeled mock data.

### Option B — local development

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # add GEMINI_API_KEY, MONGODB_URI, JWT_SECRET
uvicorn app.main:app --reload

# Web
cd frontend
npm install
npm run dev            # http://localhost:5173, proxies to :8000 via VITE_API_URL

# Mobile
cd mobile
npm install
npx expo start         # Android emulator reaches host at 10.0.2.2:8000
```

### Tests

```bash
cd backend && python -m pytest -q     # 43 passed
cd frontend && npm run lint && npm run build
cd mobile && npx expo lint && npx expo-doctor
```

## Environment variables (backend/.env)

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key. Empty → AI endpoints fail honestly with 503 (or mock only if `ALLOW_MOCK_AI=true`). |
| `MONGODB_URI` | MongoDB connection string. Empty → in-memory store (data lost on restart). |
| `JWT_SECRET` | Token signing secret — required in production; generate with `openssl rand -hex 32`. |
| `ALLOW_MOCK_AI` | `true` enables labeled mock AI for local development. Default `false`. |
| `CORS_ORIGINS` | Comma-separated allowed origins for the web app. |
| `DEBUG` | Verbose errors. Keep `false` in production. |

Web: `VITE_API_URL` (build-time API base URL).

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — components, data flow, storage/AI abstraction
- [docs/API.md](docs/API.md) — endpoint reference
- [docs/SECURITY.md](docs/SECURITY.md) — threat model and mitigations
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Docker, EAS mobile builds, prod checklist
- [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) — original audit + hardening plan
