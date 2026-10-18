"""
Shared error types and safe client-facing error envelopes.
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error with a safe, user-facing message."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "bad_request",
        detail: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        # detail is developer-facing; only included when DEBUG=true.
        self.detail = detail


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(message, status_code=404, code="not_found", detail=detail)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required", detail: Optional[str] = None):
        super().__init__(message, status_code=401, code="unauthorized", detail=detail)


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have access to this resource", detail: Optional[str] = None):
        super().__init__(message, status_code=403, code="forbidden", detail=detail)


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests. Please slow down and try again shortly.", detail: Optional[str] = None):
        super().__init__(message, status_code=429, code="rate_limited", detail=detail)


class UpstreamAIError(AppError):
    """Gemini/provider failure surfaced safely to clients."""

    def __init__(self, message: str, code: str = "ai_unavailable", detail: Optional[str] = None, status_code: int = 502):
        super().__init__(message, status_code=status_code, code=code, detail=detail)


def error_body(exc: AppError, include_detail: bool = False) -> Dict[str, Any]:
    """Build the standard error response body."""
    body: Dict[str, Any] = {"success": False, "error": exc.message, "code": exc.code}
    if include_detail and exc.detail:
        body["detail"] = exc.detail
    return body
