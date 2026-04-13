"""
INTENTA — JWT Utilities
Signed token creation and verification using python-jose (RS256-ready, HS256 default).
Token payload carries: sub (email), role, iat, exp.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.logger import get_logger

logger = get_logger("jwt")

# ── Secret & Algorithm ──────────────────────────────────────────────────────
# Load from env; fall back to a strong local default ONLY for dev.
# In production, set JWT_SECRET to a long random string (e.g. `openssl rand -hex 32`).
_SECRET_KEY: str = os.environ.get(
    "JWT_SECRET",
    "intenta-local-dev-secret-change-in-production-abc123xyz"
)
_ALGORITHM = "HS256"
_DEFAULT_EXPIRE_MINUTES = 120  # 2 hours


# ── Public API ──────────────────────────────────────────────────────────────

def create_token(email: str, role: str, expire_minutes: int = _DEFAULT_EXPIRE_MINUTES) -> str:
    """
    Issue a signed JWT.
    Payload: sub=email, role=role, iat=now, exp=now+expire_minutes.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    token = jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)
    logger.info("jwt_issued", email=email, role=role, expire_minutes=expire_minutes)
    return token


def verify_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.
    Raises ValueError on invalid / expired tokens — never returns partial data.
    """
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        if not payload.get("sub"):
            raise ValueError("Token missing subject")
        return payload
    except JWTError as e:
        logger.warning("jwt_invalid", error=str(e))
        raise ValueError(f"Invalid token: {e}") from e
