"""
LabLine Healthcare Diagnostic API
Main application entry point with modular layered architecture.
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from config import settings
from database import Base, engine, SessionLocal
import models
from services.seed_service import seed_initial_data
from middleware.security import SecurityHeadersMiddleware
from middleware.rate_limit import AuthRateLimitMiddleware
from utils.logger import logger
from routers import (
    auth_router,
    tests_router,
    bookings_router,
    payments_router,
    results_router,
    reports_router,
    analytics_router,
    user_data_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler for startup initialization and shutdown cleanup."""
    logger.info("Initializing LabLine platform database tables and catalog...")
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    logger.info("LabLine startup sequence completed successfully.")
    yield
    logger.info("LabLine platform shutting down.")


app = FastAPI(
    title="LabLine Healthcare Diagnostic API",
    description="Backend REST API for LabLine Specimen & Diagnostic Management Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|.*\.vercel\.app|.*\.onrender\.com|.*\.railway\.app|.*\.netlify\.app|.*\.fly\.dev)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Defensive Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Authentication Rate Limiter (brute force protection)
app.add_middleware(AuthRateLimitMiddleware)


# Centralized Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Consistent JSON response format for HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Safely log unhandled server exceptions without leaking internal stack traces."""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact laboratory support."},
    )


# Register Core Feature Routers
app.include_router(auth_router.router)
app.include_router(tests_router.router)
app.include_router(bookings_router.router)
app.include_router(payments_router.router)
app.include_router(results_router.router)
app.include_router(reports_router.router)
app.include_router(analytics_router.router)
app.include_router(user_data_router.router)


# Health Check Endpoints (for cold-start detection and uptime monitoring)
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint probing database connectivity and cold-start state."""
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as ex:
        db_status = f"unreachable ({str(ex)})"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "LabLine Healthcare Diagnostic API",
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
    }


# Static Frontend Delivery for Single-Origin Deployment
_frontend_candidates = [
    os.getenv("FRONTEND_DIR"),
    str(Path(__file__).resolve().parent.parent / "frontend"),
    str(Path(__file__).resolve().parent / "frontend"),
    "/app/frontend",
]
_frontend_path = next((p for p in _frontend_candidates if p and Path(p).is_dir()), None)

if _frontend_path:
    # Serves the complete frontend portal seamlessly alongside API routes
    app.mount("/", StaticFiles(directory=_frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "service": "LabLine Diagnostic API",
            "status": "operational",
            "version": "1.0.0",
            "docs": "/docs",
        }
