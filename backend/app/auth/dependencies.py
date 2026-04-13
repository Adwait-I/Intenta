"""
INTENTA — Auth Dependencies
FastAPI dependency injection for JWT-gated routes and RBAC guards.

Usage:
    @router.get("/me")
    async def me(user = Depends(get_current_user)):
        ...

    @router.get("/admin-only")
    async def admin(user = Depends(require_role("admin"))):
        ...
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import verify_token
from app.auth.repository import find_user_by_email
from app.core.logger import get_logger

logger = get_logger("auth_deps")

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """
    Validate Bearer token and return the user document from MongoDB.
    Raises HTTP 401 if the token is missing, invalid, or expired.
    Raises HTTP 403 if the account is deactivated.
    """
    try:
        payload = verify_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload["sub"]
    user = await find_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )

    return user


def require_role(*roles: str):
    """
    Factory dependency that enforces role membership.
    Example: Depends(require_role("admin"))
    """
    async def _guard(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            logger.warning(
                "rbac_denied",
                email=user.get("email"),
                user_role=user.get("role"),
                required=roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}",
            )
        return user
    return _guard
