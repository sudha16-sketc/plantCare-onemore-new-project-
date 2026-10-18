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
| Credential stuffing / password guessing | Repeated `/login` attempts | Two layers, both returning identical generic 429 bodies: a per-IP cap across auth endpoints, and a per-account failed-login lockout keyed by normalized email. Failures are recorded for **unknown** emails too, so lockout behavior never reveals whether an account exists; the unknown-email path also runs one bcrypt verify against a dummy hash so response timing matches the wrong-password path. Successful login resets the per-account counter. |
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

1. **Login limiter scope** — the per-IP cap and per-account lockout are
   in-process (same deployment model as the AI limiter): each uvicorn worker
   holds its own counters, so a multi-worker deployment multiplies the
   effective limits by worker count. For strict global limits, back both
   trackers with a shared store (Redis/Mongo) — the interfaces
   (`RateLimiter.check`, `LoginFailureTracker.check/record/clear`) are the
   seam for that swap. Behind a proxy, ensure the client IP comes from a
   trusted header or the per-IP cap counts the proxy instead of callers.
2. **HTTPS everywhere** — JWTs are bearer tokens; deploy behind TLS only.
3. **JWT secret rotation** — no key-rotation/invalidation story yet
   (short lifetimes + revocation list would be the next step).
4. **CSP headers** — consider a Content-Security-Policy on the nginx layer.
5. **Audit logging** — auth events (register/login failures) are logged at
   app level but not persisted to a dedicated audit store.
6. **Registration conflict disclosure** — `/register` returns 409 on an
   existing email. That is a deliberate UX tradeoff shared by most
   registration flows; if strict no-enumeration is required, switch to an
   email-verification flow that responds identically for taken addresses.
