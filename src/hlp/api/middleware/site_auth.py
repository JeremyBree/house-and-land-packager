"""Site-wide password gate middleware.

When SITE_PASSWORD is set, every request must present a valid `site_access`
cookie before the response is served.  Health-check endpoints and requests
carrying a valid JWT Bearer token are exempt.
"""

import hashlib
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from hlp.config import get_settings

# Paths that are always exempt (health checks for Railway).
_EXEMPT_PATHS = {"/api/health", "/api/health/db"}

_PASSWORD_PAGE = """\
<html>
<head><title>Access Required</title></head>
<body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:system-ui;background:#f8fafc;">
  <form method="POST" action="/site-auth" style="background:white;padding:2rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);width:320px;">
    <h2 style="margin:0 0 1rem;color:#0f172a;">House &amp; Land Packager</h2>
    <p style="color:#64748b;font-size:14px;margin:0 0 1rem;">Enter the site password to continue.</p>
    <input type="password" name="password" placeholder="Site password" required
      style="width:100%;padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:14px;box-sizing:border-box;margin-bottom:1rem;">
    <button type="submit" style="width:100%;padding:8px;background:#2563eb;color:white;border:none;border-radius:6px;font-size:14px;cursor:pointer;">
      Enter Site
    </button>
    {error_html}
  </form>
</body>
</html>
"""


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class SiteAuthMiddleware(BaseHTTPMiddleware):
    """Block all access unless the visitor has the site password cookie."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()

        # Feature disabled when SITE_PASSWORD is empty.
        if not settings.site_password:
            return await call_next(request)

        path = request.url.path

        # Always allow health checks.
        if path in _EXEMPT_PATHS:
            return await call_next(request)

        # Always allow the password submission endpoint.
        if path == "/site-auth":
            return await call_next(request)

        # Allow requests that carry a JWT Bearer token (already app-authenticated).
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            return await call_next(request)

        # Check the site_access cookie.
        expected = _hash_password(settings.site_password)
        cookie_value = request.cookies.get("site_access", "")
        if cookie_value == expected:
            return await call_next(request)

        # Block: show password form.
        return HTMLResponse(
            content=_PASSWORD_PAGE.replace("{error_html}", ""),
            status_code=403,
        )
