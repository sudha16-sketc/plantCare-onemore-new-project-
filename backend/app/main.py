"""
Main FastAPI Application

Entry point for the PlantCare API. Configures CORS, error handling,
request limits, logging, and mounts all routes.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError, error_body
from app.routes import analysis, auth, files, guide, health, plants
from app.services.ppt_service import ppt_service
from app.utils.config import settings

# Root logger stays INFO; only PlantCare loggers go DEBUG in debug mode so
# third-party libraries (e.g. pymongo) do not flood the console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
if settings.debug:
    for _name in ("plantcare", "plantcare.gemini", "plantcare.guide", "plantcare.ppt", "plantcare.analysis"):
        logging.getLogger(_name).setLevel(logging.DEBUG)
logger = logging.getLogger("plantcare")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: log honest status, start generated-file cleanup."""
    logger.info("PlantCare API starting (debug=%s)", settings.debug)
    origins = settings.get_allowed_origins_list()
    logger.info("CORS origins: %s", origins)
    if not settings.gemini_api_key:
        if settings.allow_mock_ai:
            logger.warning("GEMINI_API_KEY not set — MOCK AI mode enabled (ALLOW_MOCK_AI=true)")
        else:
            logger.warning("GEMINI_API_KEY not set — AI endpoints will return 503")
    if not settings.mongodb_uri:
        logger.warning("MONGODB_URI not set — using in-memory storage (data is NOT persisted)")
    cleanup_task = await ppt_service.start_cleanup_task()
    yield
    cleanup_task.cancel()
    logger.info("PlantCare API stopped")


app = FastAPI(
    title="PlantCare API",
    description=(
        "AI-powered plant care guidance, photo analysis, plant collection, "
        "and watering reminders."
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# --- CORS: configured origins only; "*" is incompatible with credentials ---
_origins = settings.get_allowed_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_limits_and_headers(request: Request, call_next):
    """Enforce a request body size cap and add basic security headers."""
    cl = request.headers.get("content-length")
    if cl and cl.isdigit() and int(cl) > settings.max_request_bytes:
        return JSONResponse(
            status_code=413,
            content={"success": False, "error": "Request body too large", "code": "payload_too_large"},
        )
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


# --- Safe error handlers (never leak stack traces or provider details) ---


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc, include_detail=settings.debug),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # FastAPI's default detail can echo raw input values; keep only field names/messages.
    safe = [
        {"field": ".".join(str(loc) for loc in err.get("loc", []) if loc != "body"), "message": err.get("msg", "invalid")}
        for err in exc.errors()[:10]
    ]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Request validation failed",
            "code": "validation_error",
            "fields": safe,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail), "code": "http_error"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback server-side; clients get a generic message.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred" if not settings.debug else str(exc),
            "code": "internal_error",
        },
    )


# --- Routes ---
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(guide.router)
app.include_router(analysis.router)
app.include_router(plants.router)
app.include_router(files.router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "PlantCare API",
        "version": "1.1.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
        "readiness": "/ready",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
