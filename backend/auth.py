import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

try:
    _env_local = os.path.join(os.path.dirname(__file__), ".env")
    _env_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.isfile(_env_local):
        load_dotenv(_env_local)
    elif os.path.isfile(_env_root):
        load_dotenv(_env_root)
except Exception:
    pass

_raw_key = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY", "labline_super_secret_jwt_hmac_sha256_production_grade_key_minimum_48_chars")
if len(_raw_key.encode('utf-8')) < 32:
    import hashlib
    JWT_SECRET_KEY = hashlib.sha256(_raw_key.encode('utf-8')).hexdigest()
else:
    JWT_SECRET_KEY = _raw_key
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES") or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except PyJWTError:
        return None
