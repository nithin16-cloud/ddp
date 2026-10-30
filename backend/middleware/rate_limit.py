"""
Rate Limiting Middleware
In-memory sliding-window IP rate limiter protecting authentication endpoints
from brute-force and credential stuffing attacks.
"""
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from config import settings

class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Store timestamps of requests: dict[ip, list[float]]
        self.auth_history = defaultdict(list)
        self.protected_paths = {"/auth/login", "/auth/signup"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")
        
        # Only rate-limit authentication write endpoints
        if path in self.protected_paths and request.method == "POST":
            # Extract client IP
            client_ip = request.client.host if request.client else "unknown"
            # In reverse proxy (Render), use x-forwarded-for if available
            x_forwarded = request.headers.get("x-forwarded-for")
            if x_forwarded:
                client_ip = x_forwarded.split(",")[0].strip()

            now = time.time()
            window_start = now - settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
            
            # Filter timestamps to current window
            recent = [t for t in self.auth_history[client_ip] if t > window_start]
            self.auth_history[client_ip] = recent

            if len(recent) >= settings.AUTH_RATE_LIMIT_MAX_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many authentication attempts. Please wait 60 seconds before retrying.",
                        "error_code": "RATE_LIMIT_EXCEEDED"
                    },
                    headers={"Retry-After": "60"}
                )

            self.auth_history[client_ip].append(now)

        return await call_next(request)

