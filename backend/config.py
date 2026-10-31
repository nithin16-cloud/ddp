"""
LabLine Configuration Module
Centralized environment-based settings for LabLine Diagnostic Platform.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load .env if present safely without traversing to restricted parent directories
try:
    _env_local = os.path.join(os.path.dirname(__file__), ".env")
    _env_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.isfile(_env_local):
        load_dotenv(_env_local)
    elif os.path.isfile(_env_root):
        load_dotenv(_env_root)
except Exception:
    pass

class Settings:
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    DEBUG: bool = ENVIRONMENT != "production"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./labline.db")

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "labline_super_secret_jwt_key_2026_clinical_security_vault")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Initial Administrator Account
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL") or os.getenv("LABLINE_ADMIN_EMAIL") or "nithin@gmail.com"
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD") or os.getenv("LABLINE_ADMIN_PASSWORD") or "12345678"

    # Initial Technician Account
    TECH_EMAIL: str = os.getenv("TECH_EMAIL") or os.getenv("LABLINE_TECH_EMAIL") or "yashas@gmail.com"
    TECH_PASSWORD: str = os.getenv("TECH_PASSWORD") or os.getenv("LABLINE_TECH_PASSWORD") or "12345678"

    # CORS Allowed Origins
    DEV_ORIGINS: List[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @property
    def allowed_origins(self) -> List[str]:
        origins = list(self.DEV_ORIGINS)
        frontend_base = os.getenv("FRONTEND_BASE_URL", "").strip().rstrip("/")
        if frontend_base and frontend_base not in origins:
            origins.append(frontend_base)

        extra = os.getenv("ALLOWED_ORIGINS", "").strip()
        if extra:
            for o in extra.split(","):
                o = o.strip().rstrip("/")
                if o and o not in origins:
                    origins.append(o)
        return origins

    # Rate Limiting Settings
    AUTH_RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("AUTH_RATE_LIMIT_MAX_REQUESTS", "30"))
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("AUTH_RATE_LIMIT_WINDOW_SECONDS", "60"))

settings = Settings()
