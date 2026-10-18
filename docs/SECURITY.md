# Security

## Threat model (what we defend against)

| Threat | Vector | Mitigation |
|--------|--------|------------|
| Credential theft at rest | DB/file compromise | bcrypt (cost 12) — passwords never stored or logged in plaintext; JWTs carry only a user id |
| Token forgery | Stolen/forged JWT | HS256 signature with server-side `JWT_SECRET`; expiry enforced; secret never leaves the server |
| Privilege escalation via request body | Forged `user_id` in payloads | Identity is **always** read from the verified token (`get_current_user`); body `user_id` fields are ignored for authorization |
| Cross-user data access | Guessing/using another user's plant id | Every collection query is filtered by the token's user id; foreign ids return 404 |
| Reversible "auth" (original bug) | `btoa()` + localStorage | Removed entirely; both clients now use real JWT login |
| Secrets in client bundles | `VITE_*` / app config | Only public config (API base URL) reaches clients; `GEMINI_API_KEY`, `JWT_SECRET`, `MONGODB_URI` are server-only |
| API key exfiltration via URLs | Key in query strings (original code did this) | Official `google-genai` SDK with header-based auth; key never appears in URLs or logs |
| Silent fake AI output | Missing key silently returning mocks | Default posture is fail-loud **503**; mocks require explicit `ALLOW_MOCK_AI=true` and are labeled `source: "mock"` / `ai_source: "mock"` in responses |
| Path traversal on PPT downloads | `../../etc/passwd` style names | Filenames slugified at generation; download route validates with a safe-path check; outside-directory names 404 |
| Malicious uploads | Oversized/spoofed files | MIME allow-list (jpeg/png/webp) **and** magic-byte sniffing; 8 MB cap (413/415/400); multipart handled by python-multipart |
| Brute force on AI endpoints | Key/credit exhaustion | Per-IP sliding-window rate limit on AI routes only (429); auth has its own login hardening via bcrypt cost |
| XSS via AI content | Model output rendered in UI | React escapes by default; no `dangerouslySetInnerHTML` anywhere in the codebase |
| CORS abuse | Cross-origin browser calls | Explicit origin allow-list from `CORS_ORIGINS`; no `*` when credentials/tokens are involved |
| Error-based info leaks | Stack traces to clients | Global handlers return generic messages when `DEBUG=false`; details go to server logs only |
| Dependency drift | Unpinned deps | Runtime `requirements.txt` fully pinned; lockfiles committed for web (`package-lock.json`) and mobile |

## Configuration hardening

- `JWT_SECRET` defaults to empty; any auth operation (token create/decode)
  fails hard with an explicit server-side error until it is configured —
  the sample `.env.example` contains only a placeholder, never a real value.
- `.gitignore` blocks `.env` (and `.env.*` except `.env.example`) at the
  repo root; both `.dockerignore` files re-block them so secrets can't enter
  image build contexts.
- Docker images run as a non-root user (`uid 10001`).
- `/ready` exposes configuration *state* (booleans/modes) but never values.

## Honest failure as a security property

Two original flaws were "fail-silent" patterns: fake auth that looked
logged-in, and mock AI that looked real. Both are now impossible by
default — the API returns explicit errors, and any mock data that does
flow (opt-in dev mode) carries a visible source label end-to-end, including
in the web/mobile UI.

## Residual risks / recommended next steps

1. **Login rate limiting** — the AI routes are rate-limited, but brute-force
   protection on `/api/v1/auth/login` (per-account lockout or per-IP limiter)
   is not yet implemented. Add before public production exposure.
2. **HTTPS everywhere** — JWTs are bearer tokens; deploy behind TLS only.
3. **JWT secret rotation** — no key-rotation/invalidation story yet
   (short lifetimes + revocation list would be the next step).
4. **CSP headers** — consider a Content-Security-Policy on the nginx layer.
5. **Audit logging** — auth events (register/login failures) are logged at
   app level but not persisted to a dedicated audit store.
