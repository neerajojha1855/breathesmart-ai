import hashlib
import hmac
import secrets
from typing import Any
from app.core.config import settings

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_token_hash(token: str, stored_hash: str) -> bool:
    computed_hash = hash_token(token)
    return hmac.compare_digest(computed_hash, stored_hash)

def generate_csrf_token() -> str:
    return secrets.token_hex(32)

def verify_csrf_token(header_token: str | None, cookie_token: str | None) -> bool:
    if not header_token or not cookie_token:
        return False
    return hmac.compare_digest(header_token, cookie_token)

def get_cookie_settings() -> dict[str, Any]:
    is_prod = settings.ENVIRONMENT.lower() == "production"
    return {
        "httponly": True,
        "samesite": "lax",
        "secure": is_prod,
        "max_age": settings.SESSION_LIFETIME_SECONDS,
        "path": "/",
    }