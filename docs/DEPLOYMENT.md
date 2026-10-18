# Deployment

## 1. Backend + web via Docker

```bash
cp backend/.env.example backend/.env
# Required for AI features:  GEMINI_API_KEY=...
# Required for auth:         JWT_SECRET=$(openssl rand -hex 32)
# Recommended:               MONGODB_URI=mongodb://... (or use --profile mongo)
# Production:                DEBUG=false, ALLOW_MOCK_AI=false,
#                            CORS_ORIGINS=https://yourdomain

docker-compose up --build -d
curl http://localhost:8000/ready    # verify storage_ok / ai_configured
```

| Service | Port | Notes |
|---------|------|-------|
| backend | 8000 | FastAPI + uvicorn, non-root image, healthcheck on `/health` |
| frontend | 3000 | nginx serving the Vite build with SPA fallback |
| mongo   | 27017 | only with `--profile mongo` |

Frontend API URL is baked at **build** time:

```bash
VITE_API_URL=https://api.yourdomain docker-compose build frontend
```

### Compose file behavior

- Secrets load from `backend/.env` via `env_file` — never commit that file.
- Generated PPTs live in the `ppt_files` volume (`/app/generated_files`).
- Images run as non-root; restart policy `unless-stopped`.

## 2. Backend without Docker

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Put a TLS-terminating reverse proxy in front (Caddy/Nginx/traefik) —
JWTs are bearer tokens; never serve auth over plain HTTP in production.

## 3. Mobile (Expo EAS)

Local APK/AAB builds require the Android SDK (not present in every dev
environment). Use EAS cloud builds instead:

```bash
cd mobile
npm install -g eas-cli && eas login
eas build:configure                       # one-time; creates eas.json project id
eas build --platform android --profile preview     # installable APK
eas build --platform android --profile production  # Play Store AAB
eas build --platform ios --profile production      # macOS signer required
```

Set the real backend URL per profile in `mobile/eas.json`:

```json
"env": { "EXPO_PUBLIC_API_URL": "https://api.yourdomain" }
```

Dev flow (device/emulator against a local backend):
- Android emulator: default `http://10.0.2.2:8000` works out of the box.
- Physical device: set `EXPO_PUBLIC_API_URL=http://<your-LAN-IP>:8000`
  and ensure the phone and host are on the same network.

## 4. Production checklist

- [ ] `DEBUG=false`, `ALLOW_MOCK_AI=false`
- [ ] `JWT_SECRET` = long random value, stored in a secrets manager
- [ ] `GEMINI_API_KEY` set → `/ready` shows `ai_configured: true`
- [ ] `MONGODB_URI` set with auth + TLS (Atlas is fine) → `storage_ok: true`
- [ ] `CORS_ORIGINS` lists exactly your web origin(s) — no wildcards
- [ ] HTTPS on every public endpoint (web + API)
- [ ] Login brute-force protection considered (see SECURITY.md residual risks)
- [ ] Backend healthcheck wired to orchestrator (`/health` liveness,
      `/ready` readiness — they intentionally differ)
- [ ] Log aggregation on the server side (errors are generic in responses
      when `DEBUG=false`, so logs are where the detail lives)
- [ ] Image rebuilds pinned to `requirements.txt` + lockfiles (no floating
      `pip install` at container start)

## 5. Verifying a deployment

```bash
curl -s https://api.yourdomain/ready | jq
# expect: storage_ok=true, ai_configured=true, mock_ai_allowed=false

curl -s -X POST https://api.yourdomain/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"smoke@example.com","username":"smoke","password":"smoketest123"}'
# expect: 201 + access_token
```
