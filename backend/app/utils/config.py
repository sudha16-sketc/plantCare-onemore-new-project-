"""
Configuration module for loading and managing environment variables.
Uses pydantic-settings for type-safe configuration management.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env in backend/).
    All secrets come from the environment — never hardcode them here.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- API keys ---
    gemini_api_key: str = ""

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    # Unsafe default was True before; production must set DEBUG=false.
    debug: bool = False

    # --- CORS ---
    # Comma-separated list of browser origins allowed to call the API.
    # "*" is rejected when credentials are enabled.
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # --- Auth ---
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    bcrypt_rounds: int = 12

    # --- Database ---
    # When empty, the API falls back to an in-memory store (dev/demo only);
    # /ready reports storage_mode: "memory" so clients can tell.
    mongodb_uri: str = ""
    mongodb_db: str = "plantcare"
    mongodb_timeout_ms: int = 5000

    # --- AI behaviour ---
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout_seconds: float = 45.0
    # When true AND no API key is configured, guide/analysis endpoints return
    # clearly-labeled mock payloads (source="mock"). Never enable in production.
    allow_mock_ai: bool = False

    # --- Uploads / limits ---
    max_upload_bytes: int = 8 * 1024 * 1024  # 8 MB
    max_request_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_image_types: str = "image/jpeg,image/png,image/webp"

    # --- Rate limiting (AI endpoints) ---
    ai_rate_limit_requests: int = 10
    ai_rate_limit_window_seconds: int = 60

    # --- Rate limiting (auth endpoints) ---
    # Per-client-IP cap across /register + /login (shared window).
    auth_rate_limit_requests: int = 20
    auth_rate_limit_window_seconds: int = 60
    # Per-account failed-login lockout. Keyed by submitted email and
    # recorded for unknown emails too, so lockout behavior is identical
    # for existing and non-existent accounts (no enumeration oracle).
    login_max_failures: int = 5
    login_failure_window_seconds: int = 300

    # --- Generated files (PPT) ---
    generated_dir: str = "generated_files"
    generated_file_ttl_seconds: int = 3600  # clean up after 1 hour

    def get_allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string to list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    def get_allowed_image_types_list(self) -> List[str]:
        return [t.strip().lower() for t in self.allowed_image_types.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (tests can clear the cache via get_settings.cache_clear())."""
    return Settings()


# Backwards-compatible module-level instance used across the app.
settings = get_settings()
